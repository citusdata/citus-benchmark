import os
from tabnanny import check
from helper import *
import yaml
from logs import Logging
import time
import socket
import subprocess
import pickle
import threading
from threading import Event
import logging

logging.basicConfig(level=logging.NOTSET)
CONFIGFILE = "config.yml"
states = [0, 0, 0, 0, 0, 0]
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def bitwise_or(a, b):

    """ returns new list of states with bitwise or operation executed """

    if len(a) != len(b):
        raise Exception(f"length of lists are not equal\na {a}, b: {b}")

    result = []

    for i in range(len(a)):
        result.append(a[i] + b[i] - (a[i] * b[i]))

    return result


def read_config_file(configfile):

    """ read config file """

    with open(configfile, 'r') as f:

        try:
            config = yaml.safe_load(f)
            ycsb = config['ycsb']
            cluster = config['cluster']
            port = config['server']

        except yaml.YAMLError as exc:
            logging.error(exc)

    return config, ycsb, cluster, port


def get_ip(cluster):

    """ get IP from created VM """

    IP = run(f"az deployment group show --resource-group {cluster['resource']} --name {cluster['resource']} --query properties.outputs.driverPublicIp.value --output tsv".split(),
    stdout=subprocess.PIPE, shell = False).stdout

    return str(IP).split("'")[1][:-2]

# global variables
config, ycsb, cluster, port = read_config_file(CONFIGFILE)
ip = get_ip(cluster)


def send_with_pickle():

    """ sends pickled message to server """

    global server
    global states

    try:
        server.send(pickle.dumps(states))

    except:
        logging.error("Sending package to server failed")


def print_current_time():

    """ print current timestamp """

    run(["date"], shell = False)


def update_state(index):

    """ updates state """

    global states

    logging.info(f"Updating state on index {index}")
    states[index] = 1

    send_with_pickle()


def check_state(frequency, index):

    """" Checks for a certain state """

    global states

    while sum(states[:index]) != index:
        time.sleep(frequency)

    return True


def open_port():

    """ opens port on azure VM in seperate process"""

    global cluster
    global port

    run(["./open-port.sh", cluster['resource'], port['port']], shell = False)


def connect_to_socket():

    """ try to connect to local socket"""

    global server
    global ip
    global port

    PORT = int(port['port'])

    logging.info(f"Trying to connect with PORT: {PORT} and IP: {ip}")

    # connect to the server
    server.connect((ip, PORT))

    logging.debug('Connecting succeeded')


def set_received_state(message):

    global states
    current_sum = sum(states)

    try:
        msg = pickle.loads(message)

        if current_sum == 6:
            states = [0, 0, 0, 0, 0, 0]

        states = bitwise_or(msg, states)

    except Exception as e:
        logging.warning(e)

        if message == b'\x0a':
            logging.info("Heartbeat from server")

        else:
            logging.warning(f"Exception: {message}")


def check_where_to_resume():

    while True:

        # Wait for messages while connected to server
        message = server.recv(1024)

        if not message:
            break

        set_received_state(message)

    pass

def monitor_states(event: Event):

    """
    This thread connects with socket and waits for messages
    Retries until connection can be established
    """

    time.sleep(90)

    global states
    global server

    # open port for ip in the background
    open_port()
    logging.debug('Port is open')

    while not event.is_set():

        try:

            logging.info("attempting to connect with socket")
            connect_to_socket()
            logging.info("connected to socket")

            while True:

                # Wait for messages while connected to server
                message = server.recv(1024)

                if not message:
                    break

                set_received_state(message)

        except Exception as e:

            logging.warning(e)
            time.sleep(10)


class Client(object):


    def __init__(self, configfile = 'config.yml'):

        """ initializes a client instance """

        global config
        global ycsb
        global port
        global cluster

        self.IP = ip
        self.CONFIG = config
        self.YCSB = ycsb
        self.CLUSTER = cluster
        self.PORT = port['port']
        self.RESOURCE = cluster['resource']
        self.PREFIX = cluster['prefix']
        self.PGHOST = cluster['host']
        self.PGPASSWORD = cluster['pgpassword']
        self.PGPORT = cluster['port']
        self.SHARD_COUNT = ycsb['shard_count']
        self.ITERATIONS = ycsb['iterations']
        self.THREADS = [int(thread) for thread in ycsb['thread_counts'].split(',')]
        self.STATES = states


    @property
    def resource(self):
        return self.RESOURCE

    @property
    def config(self):
        return self.CONFIG

    @property
    def ycsb(self):
        return self.YCSB

    @property
    def cluster(self):
        return self.CLUSTER

    @property
    def ip(self):
        return self.IP

    @property
    def port(self):
        return self.PORT

    @property
    def prefix(self):
        return self.PREFIX

    @property
    def password(self):
        return self.PGPASSWORD

    @property
    def pghost(self):
        return self.PGHOST

    @property
    def pgport(self):
        return self.PGPORT

    @property
    def shards(self):
        return self.SHARD_COUNT

    @property
    def iterations(self):
        return self.ITERATIONS

    @property
    def threads(self):
        return self.THREADS


    def print_current_time(self):

        """ print current timestamp """

        run(["date"], shell = False)


    def sleep(self, seconds = 10):

        """
        Sleeps for x seconds
        Method is useless, just more pretty
        """

        time.sleep(seconds)


    def get_logging_instance(self, iteration, thread):

        """ generates a logging instance (from class Logging) """

        logs = Logging(iteration = iteration, resource = self.resource, prefix = self.prefix, host = self.pghost,
        password = self.password, port = self.pgport, shard_count = self.shards, current_thread = thread)

        return logs


    def prepare_monitoring(self, logs):

        """ do preperations for monitoring a run """

        self.print_current_time()

        # Wait for monitoring to be started (checks every 1 secs if index 0 contains a 2)
        check_state(1, 2)

        # truncate pg_log on every worker to reduce data size
        logs.prepare_monitor_run()

        # Send to server when monitoring started
        update_state(2)

        return logs


    def finish_monitoring(self, logs, homedir, bucket, iteration, thread):

        """
        - stop monitoring
        - gather data
        - initiate postprocessing
        """

        # Wait for state to be stopped  (checks every 1 secs if index 3 and 4 contains a 1)
        check_state(1, 5)

        # Get data from current iteration
        logs.stop_monitoring()

        os.chdir(homedir + "/storage")
        path = homedir + f"/logs/scripts/{self.RESOURCE}"

        # Push postgresql and IOSTAT data to blob
        run(["./push-to-blob.sh", f"{path}/pglogs/", bucket, f"{self.RESOURCE}/pglogs"], shell = False)
        run(["./push-to-blob.sh", f"{path}/general/", bucket, f"{self.RESOURCE}/general"], shell = False)

        # Monitoring finished, update state 0 to 1 on index 3
        update_state(5)
        logging.info("States updated")

        return f"Threadcount {thread} and iteration {iteration} finished"


    def monitor_iteration(self, homedir, bucket):

        """ for every iteration, start monitoring """

        iterations = int(self.iterations)

        for iteration in range(iterations):

            for thread in self.threads:

                logs = self.get_logging_instance(iteration, thread)

                logging.info("Wait to start monitoring")
                self.prepare_monitoring(logs)

                logging.info("Finish monitoring")
                self.finish_monitoring(logs, homedir, bucket, iteration, thread)

                os.chdir(homedir)

                # collect_data for every iteration
                collect_data(bucket)

                os.chdir(homedir)

                logging.debug(f"Monitoring finished for threadcount {thread}, iteration {iteration}")

        logging.debug("All iterations are done")


def client_thread(bucket, homedir, event: Event):

    """ thread that monitors the benchmark """

    try:

        client = Client('config.yml')

        # monitor iterations
        client.monitor_iteration(homedir, bucket)

        # set event so other thread will terminate if the deamon thread is finished
        event.set()

    except Exception as e:

        logging.warning(f"{e}")

        # end all threads
        event.set()


def collect_data(bucket):

    """ collect resulting data after all runs are finished """

    run(['python3', 'collect_data.py', bucket, drivers], shell = False)


if __name__ == "__main__":

    homedir = os.getcwd()
    bucket = sys.argv[1]
    drivers = sys.argv[2]

    try:

        event = Event()

        # State Thread
        states_thread = threading.Thread(target = monitor_states, args=([event]),  daemon = True)

        # Client Thread
        c_thread = threading.Thread(target = client_thread, args = ([bucket, homedir, event]))

        # Start Threads
        states_thread.start()
        c_thread.start()

        # wait until benchmarks are finished
        states_thread.join()
        c_thread.join()


    except KeyboardInterrupt:

         logging.warning("Stopping Execution")
         sys.exit(1)

