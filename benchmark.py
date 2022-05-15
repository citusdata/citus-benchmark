import os
import subprocess
import fire
import sys
import pandas as pd
import time
from helper import *
import Threading
import yaml

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


        def prepare_postgresql_table(self):

            """
            Executes bash script that enters psql, truncates usertable if exists and creates
            a new empty usertable
            """

            run(["./prepare-table.sh", str(self.SHARD_COUNT)], shell = False)

            print("Schema and distributed tables prepared")


        def create_sign(self, filename = "run.start"):

            """ create start file if ready to run ycsb benchmarks """

            run(['touch', filename], shell = False)


    def __init__(self, workloadname = "workloada", threads = "248", records = 1000, operations = 10000, port = "5432", database = "citus",
    outdir = "output", workloadtype = "load", workloads="workloada", iterations = 1, outputfile = "results.csv", shard_count = 16,
    workers = "2", resource = "custom", host = "localhost", prepare = 0, use_yaml = True, yaml_input = "config.yml"):

        self.HOMEDIR = os.getcwd()
        self.YCSB_WORKLOADS = ["workloada", "workloadb", "workloadc", "workloadf", "workloadd", "workloade"]
        self.THREADS = self.parse_threadcounts(threads)
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
        self.HOST = host
        self.DATABASE = database
        self.ITERATION = 1
        self.WORKERS = workers
        self.RG = resource
        self.BENCH_RECORDS = records
        self.MONITOR_RECORDS = 0

        # Set environment variables
        os.environ['DATABASE'] = self.DATABASE
        os.environ['RECORDS'] = str(self.RECORDS)
        os.environ['OPERATIONS'] = str(self.OPERATIONS)
        os.environ['PORT'] = str(self.PORT)
        os.environ['HOMEDIR'] = self.HOMEDIR

        # Install YCSB and JDBC PostgreSQL driver
        self.install_ycsb()
        self.install_jdbc()

        # if prepare table
        if prepare:
            self.prepare_postgresql_table()

        # ready to start benchmark
        self.create_sign()


    def split(bench = 0.99):

        """
        split records in BENCH%, MONITOR% amount
        default: 99%, 1%
        """

        self.BENCH_RECORDS = bench * self.RECORDS
        self.MONITOR_RECORDS = self.RECORDS - self.BENCH_RECORDS


    def copy_csv_to_local(self):

        # todo insert host
        # scp to right folder locally

        run(['python3', 'model/connect-worker.py', '--prefix=marlin', f'--resource={self.RG}', f'--password{os.getenv["PGPASSWORD"]}',
        '--host={self.HOST}', get_csv])


    def get_workload(self, wtype, workload):

        """ returns list with commands to run workload """

        if wtype == "load":

            return ['./ycsb-load.sh', workload, self.PORT, self.DATABASE, str(self.RECORDS), str(self.CURRENT_THREAD), str(self.ITERATION), str(self.WORKERS), str(self.RG)]

        else:

            return ['./ycsb-run.sh', workload, self.PORT, self.DATABASE, str(self.RECORDS), str(self.CURRENT_THREAD), str(self.OPERATIONS),  str(self.ITERATION), str(self.WORKERS), str(self.RG)]


    def psql(self, command):

        """ run commands in psql """

        run(['psql', '-c', command], shell = False)


    def set_iterations(self, i):

        self.ITERATION = i

        # Set environment var for outputdirectory
        outputdir = self.OUTDIR + f"-{i+1}"

        # Create output folder if it does not exist yet en set env variable
        run(['mkdir', '-p', outputdir], shell = False)
        os.environ['OUTDIR'] = outputdir


    def truncate_usertable(self):

        """
        truncates usertable"
        """

        self.psql("truncate usertable")


    def single_workload(self):

        """
        Runs a single ycsb workload
        """

        os.environ['WORKLOAD'] = self.WORKLOAD_NAME
        os.environ['THREAD'] = str(self.CURRENT_THREAD)
        os.environ['OPERATIONS'] = str(self.OPERATIONS)

        if self.WORKLOAD_TYPE == "load":
            # truncate or load new usertable if type is load
            self.truncate_usertable()


        if self.WORKLOAD_NAME == "workloadc":
            # for workloadc, operation count * 10
            os.environ['OPERATIONS'] = str(self.OPERATIONS * 10)

        run(self.get_workload(self.WORKLOAD_TYPE, self.WORKLOAD_NAME), shell = False)


    def run_workload(self, workloadname, workloadtype):

        """
        runs a workload and set params accordingly
        """

        self.WORKLOAD_NAME = workloadname
        self.WORKLOAD_TYPE = workloadtype
        self.single_workload()


    def single_workload_multiple_threads(self):

        """
        Runs a single ycsb workload with multiple threadcounts
        """

        for i in range(self.ITERATIONS):
            self.set_iterations()
            outputdir = self.OUTDIR + f"-{i+1}"

            for thread in self.THREADS:
                self.CURRENT_THREAD = thread
                self.run_workload(self.WORKLOAD_NAME, self.WORKLOAD_TYPE)

            print(f"Done running workloadc for iteration {i}")
            print("Generating CSV")

            # gather csv with all results
            run(['python3', 'generate-csv.py', outputdir, f"{outputdir}.csv"], shell = False)


    def citus_workload(self):

        """
        Executes loading with workloada, running with workloadc
        Multiple iterations are supported
        """

        for i in range(self.ITERATIONS):

            self.set_iterations(i)

            outputdir = self.OUTDIR + f"-{i+1}"

            for thread in self.THREADS:
                self.CURRENT_THREAD = thread
                self.run_workload("workloada", "load")
                self.run_workload("workloada", "load", "monitor")
                self.run_workload("workloadc", "run")

            print(f"Done running workloadc for iteration {i}")
            print("Generating CSV")

            # gather csv with all results
            run(['python3', 'generate-csv.py', outputdir, f"{outputdir}.csv"], shell = False)

        # Copy to local
        self.copy_csv_to_local()

        # If finished, create a run.finished file
        self.create_sign("run.finished")



    def run_ycsb_parallel()):

        """"
        Runs 2 YCSB instances in parallel.
        Based on:
        https://github.com/brianfrankcooper/YCSB/wiki/Running-a-Workload-in-Parallel
        insertstart=0
        insertcount=25000000
        Use multithreading to run workloads simultaneausly
        """"

        bench_thread = Threading.thread(self.citus_workload)
        monitor_thread = Threading.thread(self.monitor_workload)

        # Wait until both threads are finished
        bench_thread.join()
        monitor_thread.join()


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





