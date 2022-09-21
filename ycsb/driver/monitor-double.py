# This scripts is called by hyperscale-{}.bicep, which spins up DriverVM and executes script to install necessary packages
# This is the driver script ‘benchmark.py’ which is run in a tmux session (session-name = init-bench)
# Downloads and installs YCSB and JDBC driver
# Could start two parallel YCSB clients. First one runs 99.9% of records via user 'citus'
# Second client runs 0.001% of records via user 'monitor', these records are logged
# Runs specified workloads (default = workload a and c), iterates multiple times through workloads
# Stores all raw YCSB output for every workload
# Generates csv’s from every benchmark iteration

### No config file needed as this script is executed on the driver VM on Azure

import os
import fire
from helper import run
import time
from os.path import exists
import socket
import pickle
import threading
from threading import Event, Lock
import math
import sys
import logging


logging.basicConfig(level=logging.NOTSET)
lock = Lock()

# global variables
states = [0, 0, 0, 0, 0, 0]
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def force_release_lock():

    global lock

    try:
        lock.release()
        logging.debug("Lock released")

    except:
        logging.debug("Lock was already released")


def send_with_pickle():

    """ sends pickled message to server """

    global server
    global states

    try:
        lock.acquire()
        server.send(pickle.dumps(states))
        lock.release()

    except:
        print("Sending package to server failed")

    force_release_lock()


def flush():

    """ if all states are 1 then flush """

    global states
    global lock

    lock.acquire()
    states = [0, 0, 0, 0, 0, 0]
    lock.release()

    logging.debug('states flushed')


def bitwise_or(a, b):

    """ returns new list of states with bitwise or operation executed """

    if len(a) != len(b):
        raise Exception(f"length of lists are not equal\na {a} ({len(a)}), b: {b} ({len(b)})")

    result = []

    for i in range(len(a)):
        result.append(a[i] + b[i] - (a[i] * b[i]))

    return result


def is_state_valid(states, index):

    """ simple checksum to see if states are correct """

    return sum(states) == index


def print_current_time():

    """ print current timestamp """

    run(["date"], shell = False)


def update_state(index):

    """ updates state """

    global states
    global lock

    print(f"Updating state on index {index}")
    lock.acquire()
    states[index] = 1
    lock.release()
    logging.debug(f'Updated states: {states}')

    send_with_pickle()
    logging.debug(f'States send to server')



def check_state(frequency, index):

    """" Checks for a certain state """

    global states

    while not states[index]:
        time.sleep(frequency)

    return True


def connect_to_socket(server):

    """ try to connect to local socket"""

    IP = socket.gethostbyname(socket.gethostname())
    PORT = int(os.getenv("SERVERPORT"))

    server.connect((IP, PORT))


def set_received_state(message):

    global states
    global lock

    current_sum = sum(states)

    try:
        msg = pickle.loads(message)

        logging.debug(f"received states: {msg}")

        lock.acquire()
        states = bitwise_or(msg, states)
        lock.release()

        logging.debug(f"States after updated received states: {states}")


    except Exception as e:

        logging.warning(e)

        if message == b'\x0a':
            logging.info("Heartbeat from server")

        else:
            logging.warning(f"Exception: {message}")

    except:

        logging.warning(f"Exception: {message}")

    force_release_lock()


def monitor_states(event: Event):

    global server
    global states

    """
    This thread connects with socket and waits for messages
    Retries until connection can be established
    """

    while not event.is_set():

        print(f"Trying to connect with socket")

        try:

            connect_to_socket(server)
            print("connected with socket")
            send_with_pickle()

            while True:

                # Wait for messages while connected to server
                message = server.recv(1024)

                if not message:
                    break

                set_received_state(message)

        except Exception as e:

            print(f"Exception: {e}")

            time.sleep(10)


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


    def shard_workload(self):

        """ Calculate size of shards for each driver """

        shardsize = math.floor(self.RECORDS / self.DRIVERS)
        self.INSERTSTART = self.DRIVER_ID * shardsize

        if int(self.DRIVER_ID) + 1 == int(self.DRIVERS):
            self.INSERTCOUNT = shardsize + (self.RECORDS % shardsize)
        else:
            self.INSERTCOUNT = shardsize

        return self.INSERTCOUNT


    def calculate_connections(self):

        """ Calculate how many connections this driver should have to the cluster """

        connections = math.floor(self.CURRENT_THREAD / self.DRIVERS)

        if int(self.DRIVER_ID) + 1 == int(self.DRIVERS):
            return connections + (self.CURRENT_THREAD % connections)

        print(f"Calculated connections: {connections}")

        return connections


    def calculate_records(self, shardsize):

        """ calculates records for user monitor """

        self.INSERTCOUNT = int(0.999 * shardsize)
        self.INSERTCOUNT_MONITOR = shardsize - self.INSERTCOUNT
        self.INSERTSTART_MONITOR = self.INSERTSTART + self.INSERTCOUNT

        print(f"Insertcount Monitor: {self.INSERTCOUNT_MONITOR}, Insertstart Monitor: {self.INSERTSTART_MONITOR}")


    def __init__(self, workloadname = "workloada", threads = "248", records = 1000, operations = 10000, port = "5432", database = "citus",
    workloadtype = "load", workloads="workloada", iterations = 1, outputfile = "results.csv", shard_count = 16,
    workers = "2", resource = "custom", host = "localhost", parallel = False, monitorpw = "monitor", maxtime = 600, drivers = 1, id = 0):

        print("DRIVER, DRIVER_ID")
        print(drivers, id)

        self.HOMEDIR = os.getcwd()
        self.PARALLEL = parallel
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
        self.HOST = host
        self.DATABASE = database
        self.ITERATION = 1
        self.WORKERS = workers
        self.RG = resource
        self.MONITORPW = monitorpw
        self.MAXTIME = maxtime
        self.INSERTCOUNT_CITUS = 0
        self.INSERTCOUNT_MONITOR = self.RECORDS - self.INSERTCOUNT_CITUS
        self.INSERTSTART = 0
        self.MONITOR_THREADS = math.floor(workers / drivers)
        self.INSERTSTART_MONITOR = 0
        self.DRIVERS = drivers
        self.DRIVER_ID = id

        # reduce self.RECORDS to the amount of the sharded workload
        shardsize = self.shard_workload()

        # Divide threads across drivers
        self.CURRENT_THREAD = self.calculate_connections()

        # Calculate records for monitor
        self.calculate_records(shardsize)

        print(f'FINAL VALUES: \n INSERTSTART {self.INSERTSTART}, INSERTCOUNT {self.INSERTCOUNT}, THREADS {self.CURRENT_THREAD}')
        print(f'FINAL MONITOR VALUES: \n INSERTSTART {self.INSERTSTART_MONITOR}, INSERTCOUNT {self.INSERTCOUNT_MONITOR}, THREADS {self.MONITOR_THREADS}')

        # Set environment variables
        os.environ['DATABASE'] = self.DATABASE
        os.environ['RECORDS'] = str(self.RECORDS)
        os.environ['OPERATIONS'] = str(self.OPERATIONS)
        os.environ['PORT'] = str(self.PORT)
        os.environ['HOMEDIR'] = self.HOMEDIR
        os.environ['HOST'] = self.HOST
        os.environ['SHARD_COUNT'] = str(self.SHARD_COUNT)
        os.environ['ITERATION'] = str(self.ITERATION)
        os.environ['WORKERS'] = str(self.WORKERS)
        os.environ['RESOURCE'] = str(self.RG)
        os.environ['MONITORPW'] = str(self.MONITORPW)
        os.environ['MAXTIME'] = str(self.MAXTIME)
        os.environ['INSERTCOUNT'] = str(self.INSERTCOUNT)
        os.environ['INSERTCOUNT_MONITOR'] = str(self.INSERTCOUNT_MONITOR)
        os.environ['INSERTSTART_MONITOR'] = str(self.INSERTSTART_MONITOR)
        os.environ['INSERTSTART'] = str(self.INSERTSTART)
        os.environ['THREADS'] = str(self.CURRENT_THREAD)
        os.environ['HOMEDIR'] = self.HOMEDIR
        os.environ['PARALLEL'] = str(self.PARALLEL)
        os.environ['PART'] = str(self.DRIVER_ID)
        os.environ['DRIVERS'] = str(self.DRIVERS)
        os.environ['MONITOR_THREADS'] = str(self.MONITOR_THREADS)

        # Install YCSB and JDBC PostgreSQL driver
        self.install_ycsb()
        self.install_jdbc()


    def get_workload(self, wtype):

        """ returns list with commands to run workload """

        if wtype == "load":

            return ['./ycsb-load.sh']

        else:

            return ['./ycsb-run.sh']


    def run_ycsb_parallel(self, wtype):

        """
        Runs 2 YCSB instances in parallel.
        Based on:
        https://github.com/brianfrankcooper/YCSB/wiki/Running-a-Workload-in-Parallel
        insertstart = 0
        insertcount = # Records
        records >= insertstart + insertcount
        """

        if wtype == "load":

            return ['./parallel-ycsb-load.sh']

        else:

            return ['./parallel-ycsb-run.sh']


    def psql(self, command):

        """ run commands in psql """

        run(['psql', '-c', command], shell = False)


    def set_iterations(self, i):

        self.ITERATION = i
        os.environ['ITERATION'] = str(self.ITERATION)


    def set_current_thread(self, thread):

        self.CURRENT_THREAD = thread
        os.environ['THREAD'] = str(self.CURRENT_THREAD)


    def set_insertcount_monitor(self):

        self.INSERTCOUNT_MONITOR = self.INSERTCOUNT_MONITOR


    def truncate_usertable(self):

        """
        truncates usertable"
        """

        self.psql("truncate usertable")


    def single_workload(self, parallel = False):

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

        if parallel:
            run(self.run_ycsb_parallel(self.WORKLOAD_TYPE), shell = False)
            return

        run(self.get_workload(self.WORKLOAD_TYPE), shell = False)


    def run_workload(self, workloadname, workloadtype, parallel = False):

        """
        runs a workload and set params accordingly
        """

        os.chdir(self.HOMEDIR + '/scripts')
        self.WORKLOAD_NAME = workloadname
        self.WORKLOAD_TYPE = workloadtype
        self.single_workload(parallel)
        os.chdir(self.HOMEDIR)


    def test_parallel_load(self):

        """ For testing a parallel load """

        # go to folder for scripts
        os.chdir("scripts")

        self.run_workload("workloada", "load", parallel = True)

        os.chdir(self.HOMEDIR)

        # If finished, create a run.finished file
        self.create_sign("run.finished")


    def single_workload_multiple_threads(self):

        """
        Runs a single ycsb workload with multiple threadcounts
        """

        for i in range(self.ITERATIONS):
            os.chdir(self.HOMEDIR + '/scripts')
            self.set_iterations()
            outputdir = self.OUTDIR + f"-{i+1}"

            for thread in self.THREADS:
                self.CURRENT_THREAD = thread
                self.run_workload(self.WORKLOAD_NAME, self.WORKLOAD_TYPE)

            print(f"Done running workloadc for iteration {i}")
            os.chdir(self.HOMEDIR)
            print("Generating CSV")

            # gather csv with all results after each iteration
            run(['python3', 'output.py', outputdir, f"results"], shell = False)


    def citus_workload(self):

        """
        Executes loading with workloada, running with workloadc
        Multiple iterations are supported
        """

        # create sign if benchmark can start
        self.create_sign()
        time.sleep(20)

        for i in range(self.ITERATIONS):
            os.chdir(self.HOMEDIR + '/scripts')
            self.set_iterations(i)

            for thread in self.THREADS:
                self.CURRENT_THREAD = thread
                os.environ['THREADS'] = str(self.CURRENT_THREAD)

                if self.PARALLEL:
                    self.run_workload("workloada", "load", self.PARALLEL)
                    self.run_workload("workloadc", "run", self.PARALLEL)
                else:
                    self.run_workload("workloada", "load")
                    self.run_workload("workloadc", "run")

            print(f"Done running workloadc for iteration {i}")
            print("Generating CSV")

            # gather csv with all results
            os.chdir(self.HOMEDIR)
            run(['python3', 'output.py', f"results"], shell = False)


    def update_and_check_state_change(self, update_index, check_index, frequency = 2):

        """ updates the states and subsequently wait for a respons from the client if the client is ready """

        update_state(update_index)
        check_state(frequency, check_index)


    def monitor_workload(self, workload, type, thread, i):

        """
        Wrapper for monitoring any workload
        """

        # send data to server because ready to start benchmarks
        self.update_and_check_state_change(0, 2, 1)

        self.set_insertcount_monitor()
        self.run_workload(workload, type, self.PARALLEL)

        # If workload finished, send a message to the server
        # update csv after every workload
        run(['python3', 'output.py', f"results"], shell = False)
        self.update_and_check_state_change(3, 5, 3)
        print(f"Execution iteration {i} finished with threadcount {thread}.\n Going to next configuration")
        flush()

        # set states to [0, 0, 0, 0]

    def execute_workloada_monitor_workloadc(self, thread, i):

        """ Loads data with workload a, monitors workload c """

        self.monitor_workload("workloada", "load", thread, i)
        self.monitor_workload("workloadc",  "run", thread, i)



    def monitor_workloadc(self):

        """
        Executes loading with workloada in a regular fashion
        Monitors workload c
        """

        for i in range(self.ITERATIONS):
            self.set_iterations(i)

            for thread in self.THREADS:
                self.set_current_thread(thread)
                self.execute_workloada_monitor_workloadc(thread, i)

            print(f"Done running workloadc for iteration {i}")
            print("Generating CSV")

            # gather csv with all results
            run(['python3', 'output.py', f"results"], shell = False)


    def monitor_workloada(self):

        """
        Monitors workload a
        """

        for i in range(self.ITERATIONS):
            self.set_iterations(i)

            for thread in self.THREADS:
                self.set_current_thread(thread)
                self.monitor_workload("workloada", "load", thread, i)

            print(f"Done running workloadc for iteration {i}")
            print("Generating CSV")

            # gather csv with all results
            run(['python3', 'output.py', f"results"], shell = False)


    def run_all_workloads(self):

        """
        Runs all workloads in the order as described in: https://github.com/brianfrankcooper/YCSB/wiki/Core-Workloads
        under "Running the workloads"
        Needs to be refactored
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

            print("Done running all YCSB core workloads")
            os.chdir(self.HOMEDIR)
            print("Generating CSV")

            # gather csv with all results
            run(['python3', 'output.py', f"results"], shell = False)



def initiate_benchmarks(event: Event):

    try:

        fire.Fire(Benchmark)

        # finish threads
        event.set()

    except:
        event.set()


def heartbeat(event: Event, frequency = 60):

    global states

    while not event.is_set():

        try:
            send_with_pickle()

        except:
            logging.warning("Failed to send states to server")

        time.sleep(frequency)


if __name__ == '__main__':

    try:

        # Set event
        event = Event()

        # State Thread, monitors state and communicates with socket
        states_thread = threading.Thread(target = monitor_states, args=([event]),  daemon = True)

        # Heartbeat Thread, sends heartbeats to server
        heartbeat = threading.Thread(target = heartbeat, args=([event]),  daemon = True)

        # Benchmark Thread
        benchmark_thread = threading.Thread(target = initiate_benchmarks, args=([event]))

        # Start Threads
        states_thread.start()
        benchmark_thread.start()
        heartbeat.start()

        # wait until benchmarks are finished
        states_thread.join()
        benchmark_thread.join()
        heartbeat.join()


    except KeyboardInterrupt:

         run(['python3', 'output.py', f"results"], shell = False)
         sys.exit(1)






