import os
import fire
from helper import run

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
                raise ValueError('Error: Invalid input, please enter integers in format "300" or "300,400" if multiple threadcounts')

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


    def usertable(self):

        """ usertable schema for ycsb benchmarks """

        run(['./usertable.sh'], shell = False)


    def __init__(self, workloadname = "workloada", threads = "248", records = 1000, operations = 10000, port = "5432", database = "citus",
    workloadtype = "load", workloads="workloada", iterations = 1, outputfile = "results.csv", shard_count = 16,
    workers = "2"):

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
        self.OUTDIR = "results"
        self.OUTPUTFILE = outputfile
        self.CURRENT_THREAD = self.THREADS[0]
        self.ITERATIONS = iterations
        self.DATABASE = database
        self.ITERATION = 1
        self.WORKERS = workers

        # Set environment variables
        os.environ['DATABASE'] = self.DATABASE
        os.environ['RECORDS'] = str(self.RECORDS)
        os.environ['OPERATIONS'] = str(self.OPERATIONS)
        os.environ['PORT'] = str(self.PORT)
        os.environ['SHARD_COUNT'] = str(self.SHARD_COUNT)
        os.environ['ITERATION'] = str(self.ITERATION)
        os.environ['WORKERS'] = str(self.WORKERS)
        os.environ['THREADS'] = str(self.CURRENT_THREAD)
        os.environ['HOMEDIR'] = self.HOMEDIR

        # Install YCSB and JDBC PostgreSQL driver
        self.install_ycsb()
        self.install_jdbc()

        # YCSB schema for citus

        os.chdir(self.HOMEDIR + '/scripts')
        self.usertable()
        os.chdir(self.HOMEDIR)


    def get_workload(self, wtype):

        """ returns list with commands to run workload """

        if wtype == "load":

            return ['./ycsb-load.sh']

        else:

            return ['./ycsb-run.sh']


    def psql(self, command):

        """ run commands in psql """

        run(['psql', '-c', command], shell = False)


    def set_iterations(self, i):

        self.ITERATION = i
        os.environ['ITERATION'] = str(self.ITERATION)


    def set_current_thread(self, thread):

        self.CURRENT_THREAD = thread
        os.environ['THREAD'] = str(self.CURRENT_THREAD)


    def truncate_usertable(self):

        """
        truncates usertable
        """

        self.psql("truncate usertable")


    def single_workload(self):

        """
        Runs a single ycsb workload
        """

        os.environ['WORKLOAD'] = self.WORKLOAD_NAME
        os.environ['THREAD'] = str(self.CURRENT_THREAD)
        os.environ['OPERATIONS'] = str(self.OPERATIONS)
        os.environ['WORKLOAD_TYPE'] = self.WORKLOAD_TYPE

        if self.WORKLOAD_TYPE == "load":
            # truncate or load new usertable if type is load
            self.truncate_usertable()

        if self.WORKLOAD_NAME == "workloadc":
            # for workloadc, operation count * 10
            os.environ['OPERATIONS'] = str(self.OPERATIONS * 10)

        run(self.get_workload(self.WORKLOAD_TYPE), shell = False)


    def run_workload(self, workloadname, workloadtype):

        """
        runs a workload and set params accordingly
        """

        os.chdir(self.HOMEDIR + '/scripts')
        self.WORKLOAD_NAME = workloadname
        self.WORKLOAD_TYPE = workloadtype
        self.single_workload()
        os.chdir(self.HOMEDIR)


    def create_csv(self):
        """ generates a csv from ycsb output """

        run(['python3', 'generate_csv.py', f'{os.getenv["RESOURCE"]}-results.csv'], shell = False)


    def loada(self):
        """ load workload a """

        self.run_workload("workloada", "load")


    def loade(self):
        """ load workload e """

        self.run_workload("workloade", "load")


    def run_single_workload(self, workload):

        for i in range(self.ITERATIONS):

            self.set_iterations(i)

            for thread in self.THREADS:
                self.CURRENT_THREAD = thread
                os.environ['THREADS'] = str(self.CURRENT_THREAD)

                if workload.lower() is "workloade":
                    self.loade()
                else:
                    self.loada()

                self.run_workload(workload, "run")

            self.create_csv()


    def workloada(self):

        """ run workload a """

        self.run_single_workload("workloada")


    def workloadb(self):
        """ run workload b """

        self.run_single_workload("workloadb")


    def workloadc(self):
        """ run workload c """

        self.run_single_workload("workloadc")


    def workloadf(self):
        """ run workload f """

        self.run_single_workload("workloadf")


    def workloadd(self):
        """ run workload d """

        self.run_single_workload("workloadd")


    def workloade(self):
        """ run workload e """

        self.run_single_workload("workloade")


    def run_all_workloads(self):

        """
        Runs all workloads in the order as described in: https://github.com/brianfrankcooper/YCSB/wiki/Core-Workloads
        under "Running the workloads"
        """

        for i in range(self.ITERATIONS):

            os.chdir(self.HOMEDIR + '/scripts')

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

            os.chdir(self.HOMEDIR)

            print(f"Done with iteration {i}")

            # gather csv with all results
            run(['python3', 'generate_csv.py', "results.csv"], shell = False)


if __name__ == '__main__':

    try:
        fire.Fire(Benchmark)

    except KeyboardInterrupt:
         run(['python3', 'generate_csv.py', f'{os.getenv["RESOURCE"]}-results.csv'], shell = False)

    # if benchmarks are finished, create token
    run(['touch', 'benchmarks.finished'], shell = False)






