import sys
import subprocess
import os
import datetime
import fire

MAX_THREADS = 1000
MIN_THREADS = 1
CHECK_FREQUENCY_IN_SECONDS = 10

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

    def check_if_thread_is_int(self, thread):

        """
        Check whether given input is a valid integer
        """

        global MAX_THREADS
        global MIN_THREADS

        try:
                if int(thread) > MAX_THREADS:
                    raise ValueError(f'Invalid input, threadcount exceeds maximum of {MAX_THREADS}')

                elif int(thread) < MIN_THREADS:
                    raise ValueError(f'Invalid input, threadcount exceeds minimum of {MIN_THREADS}')

        except:
                raise ValueError('Invalid input, please enter integers in format "300" or "300,400" if multiple threadcounts')

        return thread


    def parse_threadcounts(self, thread_counts):

        """
        Parses string of threadcounts and returns list
        """

        try:

            int(thread_counts)
            return self.check_if_thread_is_int(thread_counts)

        except:
            return ','.join([str(self.check_if_thread_is_int(thread)) for thread in thread_counts])


    def set_shard_count(self, workers, shards):

        if not shards:
            return 2 * int(workers)

        return shards


    def __init__(self, resource, threads = "248", records = 1000, operations = 10000, database = "citus",  workloads = "run_all_workloads",
    iterations = 1, workers = "2", shard_count = 0, autodelete = False, deployment = "hyperscale-ycsb"):

        self.THREADS = self.parse_threadcounts(threads)
        self.RECORDS = records
        self.OPERATIONS = operations
        self.ITERATIONS = iterations
        self.WORKERS = workers
        self.SHARD_COUNT = self.set_shard_count(workers, shard_count)
        self.DATABASE = database
        self.RG = resource
        self.DEPLOYMENT = deployment
        self.AUTO = autodelete
        self.WORKLOAD_FUNCTION = workloads

        # Set environment variables
        os.environ['HOMEDIR'] = os.getcwd()
        os.environ['PGDATABASE'] = self.DATABASE
        os.environ['RESOURCE'] = self.RG
        os.environ['SHARD_COUNT'] = str(self.SHARD_COUNT)
        os.environ['ITERATIONS'] = str(self.ITERATIONS)
        os.environ['WORKERS'] = str(self.WORKERS)
        os.environ['RECORDS'] = str(self.RECORDS)
        os.environ['THREADS'] = str(self.THREADS)
        os.environ['WORKLOADS'] = str(self.WORKLOAD_FUNCTION)
        os.environ['OPERATIONS'] = str(self.OPERATIONS)


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


    def start_benchmark(self):

        """ initiates benchmark run and corresponding infrastructure """

        global CHECK_FREQUENCY_IN_SECONDS

        print(datetime.datetime.now())

        # start the benchmark
        run(['./start-benchmark-ycsb.sh', self.resource, self.deployment], shell = False)

        try:
            run(['./wait-for-results-ycsb.sh', 'benchmarks.finished', str(CHECK_FREQUENCY_IN_SECONDS)], shell = False)

        except KeyboardInterrupt:
            run(['./get-file.sh', f'{self.resource}-results.csv'], shell = False)

        # Delete cluster if autodelete is set to true
        if self.autodelete:
                run(['./cleanup.sh', self.resource], shell = False)


if __name__ == '__main__':

    benchmark = fire.Fire(StartBenchmark)



