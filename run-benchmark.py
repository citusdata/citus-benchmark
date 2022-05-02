import os
import subprocess
import fire
import sys
import pandas as pd
import time

def eprint(*args, **kwargs):

    """
    eprint prints to stderr
    """

    print(*args, file=sys.stderr, **kwargs)


def run(command, *args, shell=True, **kwargs):

    """
    run runs the given command and prints it to stderr
    """
    
    eprint(f"+ {command} ")
    result = subprocess.run(command, *args, check=True, shell=shell, **kwargs)

    return result


class Benchmark(object):

    def check_workloadname(self, workloadname):

            """ Check if workloadname in workloads """

            if workloadname.lower() not in set(self.YCSB_WORKLOADS):
                raise ValueError(f"Invalid input: '{workloadname}'. Choose existing workload(s): {self.YCSB_WORKLOADS}")

            return workloadname.lower()


    def parse_workloads(self, workloads):

        """
        parses string of workloads seperated by a comma
        returns list of workloads
        """

        if type(workloads) == str:
            return [self.check_workloadname(workloads)]

        # Raise error if there are any workloads that do not exist
        if workloads.intersection(set(self.YCSB_WORKLOADS)) != workloads:
            raise ValueError(f"Invalid input: '{workloads}'. Choose existing workload(s): {self.YCSB_WORKLOADS}")

        # Remove repeated workloads
        return list(set(workloads))


    def check_if_int(self, threads):

        """
        Check whether given input is a valid integer        
        """

        try:
                int(threads)
        except:
                raise ValueError('Error: Invalid input, please enter integers in format "300" or "300;400" if multiple threadcounts')

        return int(threads)


    def parse_threadcounts(self, thread_counts):

        """
        Parses string of threadcounts and returns list 
        """

        if type(thread_counts) == int:
            return [thread_counts]

        return [self.check_if_int(thread) for thread in thread_counts]


    def install_ycsb(self):

        """ install YCSB """

        # Check if ycsb directory exists
        if os.path.isdir('ycsb-0.17.0'):
            return
        
        # get ycsb and unpack
        run(['wget', 'https://github.com/brianfrankcooper/YCSB/releases/download/0.17.0/ycsb-0.17.0.tar.gz'], shell = False)
        run(['tar', 'xfvz', 'ycsb-0.17.0.tar.gz'], shell = False)


    def install_jdbc(self):

        """ install JDBC PostgreSQL driver """

        # Check if postgresql jdbc driver exists
        if os.path.isfile('ycsb-0.17.0/postgresql-42.2.14.jar'):
            return

        os.chdir("ycsb-0.17.0")
        run(['wget', 'https://jdbc.postgresql.org/download/postgresql-42.2.14.jar'], shell = False)
        os.chdir(self.HOMEDIR)


    def __init__(self, workloadname = "workloada", threads = "248", records = 1000, operations = 10000, port = "5432", database = "citus",
    outdir = "output", workloadtype = "load", workloads="workloada", iterations = 1, outputfile = "results.csv", shard_count = 16):

        self.HOMEDIR = os.getcwd()
        self.THREADS = self.parse_threadcounts(threads)
        self.YCSB_WORKLOADS = ["workloada", "workloadb", "workloadc", "workloadf", "workloadd", "workloade"]
        self.RECORDS = records
        self.OPERATIONS = operations
        self.SHARD_COUNT = shard_count
        self.PORT = str(port)
        self.WORKLOAD_LIST = self.parse_workloads(workloads)
        self.WORKLOAD_NAME = self.check_workloadname(workloadname)
        self.WORKLOAD_TYPE = workloadtype
        self.OUTDIR = outdir
        self.OUTPUTFILE = outputfile
        self.CURRENT_THREAD = self.THREADS[0]
        self.ITERATIONS = iterations
        self.HOST = "localhost"
        self.DATABASE = database

        # Set environment variables
        os.environ['DATABASE'] = self.DATABASE
        os.environ['RECORDS'] = str(self.RECORDS)
        os.environ['OPERATIONS'] = str(self.OPERATIONS)
        os.environ['PORT'] = str(self.PORT) 
        os.environ['HOMEDIR'] = self.HOMEDIR

        # Install YCSB and JDBC PostgreSQL driver
        self.install_ycsb()
        self.install_jdbc()


    def get_workload(self, wtype, workload):

        """ returns list with commands to run workload """

        if wtype == "load":

            return ['./ycsb-load.sh', workload, self.PORT, self.DATABASE, str(self.RECORDS), str(self.CURRENT_THREAD)]
        
        else:
            
            return ['./ycsb-run.sh', workload, self.PORT, self.DATABASE, str(self.RECORDS), str(self.CURRENT_THREAD), str(self.OPERATIONS)]
        

    def psql(self, command):

        """ run commands in psql """

        run(['psql', '-c', command], shell = False)


    def prepare_postgresql_table(self):

        """
        Executes bash script that enters psql, truncates usertable if exists and creates 
        a new empty usertable
        """

        run(["./prepare-table.sh", str(self.SHARD_COUNT)], shell = False)

        print("Schema and distributed tables prepared")


    def truncate_usertable(self):

        """
        truncates usertable"
        """

        self.psql("truncate usertable;")
    

    def single_workload(self):

        """
        Runs a single ycsb workload
        """

        os.environ['WORKLOAD'] = self.WORKLOAD_NAME
        os.environ['THREAD'] = str(self.CURRENT_THREAD)
        os.environ['OPERATIONS'] = str(self.OPERATIONS)
        
        if self.WORKLOAD_TYPE == "load":
            # truncate or load new usertable if type is load
            self.prepare_postgresql_table()


        if self.WORKLOAD_NAME == "workloadc":
            # for workloadc, operation count * 10
            os.environ['OPERATIONS'] = str(self.OPERATIONS * 10)

        print(f"LOAD/RUN: {self.WORKLOAD_TYPE}, WORKLOAD: {self.WORKLOAD_NAME}, THREADCOUNT: {self.CURRENT_THREAD}, RECORDS: {self.RECORDS}, OPERATIONS: {self.OPERATIONS}")
        run(self.get_workload(self.WORKLOAD_TYPE, self.WORKLOAD_NAME), shell = False)


    def single_workload_multiple_threads(self):

        """
        Runs a single ycsb workload with multiple threadcounts
        """

        for thread in self.THREADS:
            self.CURRENT_THREAD = thread
            self.single_workload()


    def run_workload(self, workloadname, workloadtype):

        """
        runs a workload and set params accordingly
        """

        self.WORKLOAD_NAME = workloadname
        self.WORKLOAD_TYPE = workloadtype
        self.single_workload()

    
    def citus_workload(self):

        """
        Executes loading with workloada, running with workloadc
        Multiple iterations are supported
        """

        for i in range(self.ITERATIONS):

            # Set environment var for outputdirectory
            outputdir = self.OUTDIR + f"-{i+1}"

            # Create output folder if it does not exist yet en set env variable
            run(['mkdir', '-p', outputdir], shell = False)
            os.environ['OUTDIR'] = outputdir

            for thread in self.THREADS:
                self.CURRENT_THREAD = thread
                self.run_workload("workloada", "load")
                self.run_workload("workloadc", "run")

            print(f"Done running workloadc for iteration {i}")
            print("Generating CSV")

            # gather csv with all results
            run(['python3', 'generate-csv.py', outputdir, f"{outputdir}.csv"], shell = False)


    def run_multiple_workloads(self, workloads):

        """
        Method that runs multiple workloads in the order as described in YCSB core workloads
        """

        # if list contains only workloade then load and run workloade
        if workloads == ['workloade']:
            self.WORKLOAD_NAME = workloads[0]
            self.run_workload("workloade", "load")
            self.run_workload("workloade", "run")

        # Sort workloads in 'YCSB Core Workloads' order
        workloads = self.sort_workloads(workloads)

        # DB needs to be loaded so always load with workloada
        self.run_workload("workloade", "load")

        # Iterate through all workloads
        for workload in workloads:
            self.WORKLOAD_NAME = workload

            if self.WORKLOAD_NAME == "workloade":
                self.run_workload("workloade", "load")
                self.run_workload("workloade", "run")
                continue

            self.WORKLOAD_NAME = workload
            self.single_workload()



    def run_all_workloads(self):

        """
        Runs all workloads in the order as described in: https://github.com/brianfrankcooper/YCSB/wiki/Core-Workloads
        under "Running the workloads"
        """

        for i in range(self.ITERATIONS):

            # Set environment var for outputdirectory
            outputdir = self.OUTDIR + f"-{i+1}"

            # Create output folder if it does not exist yet en set env variable
            run(['mkdir', '-p', outputdir], shell = False)
            os.environ['OUTDIR'] = outputdir

            for thread in self.THREADS:
                self.CURRENT_THREAD = thread

                for workload in self.YCSB_WORKLOADS:
                    self.WORKLOAD_NAME = workload

                    if workload == "workloada":
                        self.run_workload("workloada", "load")
                        self.run_workload("workloada", "run")
                        continue

                    if workload == "workloade":
                        self.run_workload("workloade", "load")
                        self.run_workload("workloade", "run")
                        continue
                    
                    self.run_workload(workload, "run")
            
            print("Done running all YCSB core workloads")
            print("Generating CSV")

            # gather csv with all results
            run(['python3', 'generate-csv.py', outputdir, f"{outputdir}.csv"], shell = False)



if __name__ == '__main__':

  fire.Fire(Benchmark)





