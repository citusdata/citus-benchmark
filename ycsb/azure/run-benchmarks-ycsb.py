import sys
import subprocess
import os
import fire

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


class StartBenchmark(object):


    def check_workloadname(self, workloadname):

            """ Check if workloadname is in existing workloads """

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
        return ','.join(list(set(workloads)))


    def check_if_int(self, thread):

        """
        Check whether given input is a valid integer
        """

        try:
                if int(thread) > 1000:
                    raise ValueError('Error: Invalid input, threadcount exceeds maximum of 1000')
        except:
                raise ValueError('Error: Invalid input, please enter integers in format "300" or "300;400" if multiple threadcounts')

        return thread


    def parse_threadcounts(self, thread_counts):

        """
        Parses string of threadcounts and returns list
        """

        try:
            int(thread_counts)
            return thread_counts

        except:
            threads = thread_counts.split(',')

        return ','.join([self.check_if_int(thread) for thread in threads])


    def __init__(self, resource, threads = "248", records = 1000, operations = 10000, port = "5432", database = "citus",  workloads = "workloada", iterations = 1, workers = "2", deployment = "hyperscale-ycsb",
    out = "results", autodelete = False):

        self.YCSB_WORKLOADS = ["workloada", "workloadb", "workloadc", "workloadf", "workloadd", "workloade"]
        self.THREADS = self.parse_threadcounts(threads)
        self.RECORDS = records
        self.OPERATIONS = operations
        self.SHARD_COUNT = 2 * int(workers)
        self.WORKLOAD_LIST = self.parse_workloads(workloads)
        self.OUTDIR = out
        self.ITERATIONS = iterations
        self.WORKERS = workers
        self.DATABASE = database
        self.RG = resource
        self.DEPLOYMENT = deployment
        self.AUTO = autodelete

        # Set environment variables
        os.environ['HOMEDIR'] = os.getcwd()
        os.environ['PGDATABASE'] = self.DATABASE
        os.environ['RESOURCE'] = self.RG
        os.environ['SHARD_COUNT'] = str(self.SHARD_COUNT)
        os.environ['ITERATIONS'] = str(self.ITERATIONS)
        os.environ['WORKERS'] = str(self.WORKERS)
        os.environ['RECORDS'] = str(self.RECORDS)
        os.environ['THREADS'] = str(self.THREADS)
        os.environ['WORKLOADS'] = str(self.WORKLOAD_LIST)
        os.environ['OPERATIONS'] = str(self.OPERATIONS)

        # directory for output of results
        if not os.path.isdir(self.OUTDIR):
            os.mkdir(self.OUTDIR)


    @property
    def resource(self):
        """ get resource group """

        return self.RG


    @property
    def deployment(self):
        """ get deployment """

        return self.DEPLOYMENT


    @property
    def autodelete(self):
        """ get autodelete """

        return self.AUTO


if __name__ == '__main__':

    benchmark = fire.Fire(StartBenchmark)

    # start the benchmark
    run(['./start-benchmark-ycsb.sh', benchmark.resource, benchmark.deployment], shell = False)

    # Wait for finalization of benchmarks
    run(['./wait-for-results-ycsb.sh', benchmark.resource, 'benchmarks.finished', '10'], shell = False)

    # Delete cluster if autodelete is set to true
    if benchmark.autodelete:
            run(['./cleanup.sh', benchmark.resource], shell = False)


