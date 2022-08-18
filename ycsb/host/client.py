import os
from helper import *
import yaml
from logs import Logging
import time
import socket
import subprocess
import pickle
import threading

CONFIGFILE = "config.yml"
states = [0, 0, 0, 0]
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
it = 0


def read_config_file(configfile):

    """ read config file """

    with open(configfile, 'r') as f:

        try:
            config = yaml.safe_load(f)
            ycsb = config['ycsb']
            cluster = config['cluster']
            port = config['server']

        except yaml.YAMLError as exc:
            print(exc)

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
        print("Sending package to server failed")


def is_state_valid(states, index):

    """ simple checksum to see if states are correct """

    return sum(states) == index


def print_current_time():

    """ print current timestamp """

    run(["date"], shell = False)


def update_state(index):

    """ updates state """

    global states

    if is_state_valid(states, index):

        print(f"Updating state on index {index}")
        states[index] = 1

        send_with_pickle()

    else:
        print(f"WARNING: Invalid states '{states}' encountered")


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
    current_sum = sum(states)

    try:

        msg = pickle.loads(message)
        _sum = sum(msg)

        if  _sum > current_sum:
            states = msg
            print(f"States are updated: {msg}")

        if _sum == 0 and current_sum == 4:
            states = [0, 0, 0, 0]

        if _sum < current_sum:
            send_with_pickle()

    except:

        print(f"Exception: {pickle.loads(message)}")


def monitor_states():

    global server
    global states

    """
    This thread connects with socket and waits for messages
    Retries until connection can be established
    """

    while True:

        print(f"Trying to connect with socket")

        try:

            connect_to_socket(server)

            while True:

                # Wait for messages while connected to server
                message = server.recv(1024)

                if not message:
                    break

                set_received_state(message)

        except:

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


    def open_port(self):

        """ opens port on azure VM """

        run(['./port.sh', self.resource, self.port, '>/dev/null', '2>&1'], shell = False)


    def print_current_time(self):

        """ print current timestamp """

        run(["date"], shell = False)


    def sleep(self, seconds = 10):

        """
        Sleeps for x seconds
        Method is useless, just more pretty
        """

        time.sleep(seconds)


    # def manage_states(self, state, logs, server, homedir, bucket, iteration):

    #     """ Checks status corresponding to state """

    #     global states

    #     if state == 0:
    #         self.wait_for_data(server)

    #     if state == 1:
    #         self.start_and_sent(logs, iteration, server)

    #     if state == 2:
    #         while True:
    #             self.wait_for_data(server)
    #             self.finish_and_sent(server, logs, server, homedir, bucket, iteration)

    #     if state == 3:
    #         self.finish_and_sent(server, logs, server, homedir, bucket, iteration)

    #     elif state == 4:
    #         raise Exception(f"States are being flushed by server")

    # def manage_state(self, state, server):

    #     """Testing method: Checks states """

    #     global states

    #     print(f"Current state {state}")

    #     if state < sum(states):
    #         # if states are further then received from server
    #         # update states on server side
    #         self.send_with_pickle(server)

    #     if state == 1:
    #         print("initiating monitoring")
    #         #sb
    #         self.update_state(1, server)

    #     elif state == 2:
    #         print("do nothing")

    #     elif state == 3:
    #         print("Collect data")
    #         #sb
    #         self.update_state(3, server)

    #     else:
    #         print("do nothing")
    #         self.send_with_pickle(server)


    # def get_data(self, server):

    #     while True:

    #         message = server.recv(1024)

    #         if not message:
    #             break

    #         try:

    #             msg = pickle.loads(message)
    #             _sum = sum(msg)
    #             print(msg)

    #             global states

    #             if  _sum >= sum(states):
    #                 states = msg
    #                 print(f"New states: {msg}")
    #                 self.manage_state(_sum, server)
    #                 continue

    #             if _sum == 0 and sum(states) == 4:
    #                 states = msg
    #                 print("RESETTING STATES")
    #                 continue

    #         except:
    #             print(f"Message: {pickle.loads(message)}")

    #     self.try_to_connect_with_socket(server, "Reconnecting ... ")


    # def start_and_sent(self, logs, iteration, server):

    #     """ starts monitoring and sends sign """

    #     self.prepare_monitoring(logs, iteration, server)


    # def finish_and_sent(self, logs, server, homedir, bucket, iteration):

    #     """ finishes monitoring and sends sign """

    #     self.finish_monitoring(logs, server, homedir, bucket, iteration)


    # def create_socket(self):

    #     """ creates socket """

    #     server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     server.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

    #     return server


    # def connect_to_socket(self, server):

    #     """ try to connect to socket and wait for message from socket """

    #     server.connect((self.ip, int(self.port)))
    #     # _states = server.recv(10)

    #     # # global states
    #     # # states = _states

    #     # self.get_data(server)


    def try_to_connect_with_socket(self, message = "Connecting with socket"):

        """
        Connect with socket
        Retries until connection can be established
        """

        self.open_port()
        server = self.create_socket()

        while True:

            try:
                self.connect_to_socket(server)

            except:
                time.sleep(10)


    def get_logging_instance(self, iteration):

        """ generates a logging instance (from class Logging) """

        logs = Logging(iteration = iteration, resource = self.resource, prefix = self.prefix, host = self.pghost,
        password = self.password, port = self.pgport, shard_count = self.shards)

        return logs


    def prepare_monitoring(self, logs):

        """ do preperations for monitoring a run """

        self.print_current_time()

        # Wait for monitoring to be started (checks every 5 secs if index 0 contains a 1)
        check_state(5, 0)

        # truncate pg_log on every worker to reduce data size
        logs.prepare_monitor_run()

        # Send to server when monitoring started
        update_state(1)

        return logs


    def finish_monitoring(self, logs, homedir, bucket, iteration):

        """
        - stop monitoring
        - gather data
        - initiate postprocessing
        """

        # Wait for state to be stopped  (checks every 30 secs if index 3 contains a 1)
        check_state(30, 2)

        #### Get data from this iteration ####
        logs.stop_monitoring()

        os.chdir(homedir + "/storage")
        path = homedir + f"/logs/scripts/{self.RESOURCE}"

        # Push postgresql and IOSTAT data to blob
        run(["./push-to-blob.sh", f"{path}/pglogs/", bucket, f"{self.RESOURCE}/pglogs"], shell = False)
        run(["./push-to-blob.sh", f"{path}/general/", bucket, f"{self.RESOURCE}/general"], shell = False)

        # Monitoring finished
        update_state(3)

        return f"Iteration {iteration} finished"


    def monitor_iteration(self, homedir, bucket):

        """ for every iteration, start monitoring """

        iterations = int(self.iterations)

        for iteration in range(iterations):

            logs = self.get_logging_instance(iteration)

            print("Wait to start monitoring")
            self.prepare_monitoring(logs)

            print("Finish monitoring")
            self.finish_monitoring(logs, homedir, bucket, iteration)

            print(f"Monitoring finished for iteration {iteration}")


def client_thread(bucket, homedir):

    """ thread that monitors the benchmark """

    client = Client('config.yml')

    time.sleep(90)

    # monitor iterations
    client.monitor_iteration(homedir, bucket)

    # Collect data after iterations are finised
    os.chdir(homedir)

    collect_data(bucket)


def collect_data(bucket):

    """ collect resulting data after all runs are finished """

    run(['python3', 'collect_data.py', bucket], shell = False)


if __name__ == "__main__":

    homedir = os.getcwd()
    bucket = sys.argv[1]

    try:

        # State Thread
        states_thread = threading.Thread(target = monitor_states)

        # Client Thread
        c_thread = threading.Thread(target = client_thread, args = ([bucket, homedir]))

        # Start Threads
        states_thread.start()
        c_thread.start()

        # wait until benchmarks are finished
        c_thread.join()


    except KeyboardInterrupt:

         run(['python3', 'output.py', "results.csv"], shell = False)

