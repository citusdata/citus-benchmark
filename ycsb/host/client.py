# DRIVER SCRIPT:
# If benchmark is running, i.e. if run.start on driver then start iostat on worker nodes in tmux session cpu-usage
# Wait for benchmarks to be finished
# If benchmark finished, kill tmux sessions and remove resource metrics
# Start collecting data from driver and worker nodes

import os
from helper import *
import yaml
from logs import Logging
import time
import socket
import subprocess

class Client(object):

    def read_config_file(self, configfile):

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


    def __init__(self, configfile = 'config.yml'):

        """ initializes a client instance """

        config, ycsb, cluster, port = self.read_config_file(configfile)

        self.IP = self.get_ip(cluster)
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


    def get_ip(self, cluster):

        """ get IP from created VM """

        IP = run(f"az deployment group show --resource-group {cluster['resource']} --name {cluster['resource']} --query properties.outputs.driverPublicIp.value --output tsv".split(),
        stdout=subprocess.PIPE, shell = False).stdout

        return str(IP).split("'")[1][:-2]


    def get_config(self):

        """ returns config file """

        return self.CONFIG


    def get_ycsb(self):

        """ returns ycsb config file dict """

        return self.YCSB


    def get_cluster(self):


        """ returns cluster config file dict"""

        return self.CLUSTER


    def get_ip_adress(self):

        """ returns public ip of driver VM """

        return self.IP


    def get_port(self):

        """ returns port to connect to with server """

        return self.PORT


    def open_port(self):

        """ opens port on azure VM """

        run(['./port.sh', self.RESOURCE, self.PORT, '>/dev/null', '2>&1'], shell = False)


    def print_current_time(self):

        """ print current timestamp """

        run(["date"], shell = False)


    def sleep(self, seconds = 10):

        """
        Sleeps for x seconds
        Method is useless, just more pretty
        """

        time.sleep(seconds)


    def create_socket(self):

        """ creates socket """

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

        return server


    def connect_to_socket(self, server):

        """ try to connect to socket and wait for message from socket """

        server.connect((self.IP, int(self.PORT)))
        msg = server.recv(1024)
        print(msg.decode('UTF-8'))


    def try_to_connect_with_socket(self):

        """
        Connect with socket
        Retries until connection can be established
        """

        self.open_port()
        server = self.create_socket()

        while True:

            print("trying to connect")

            try:
                self.connect_to_socket(server)
                break

            except:
                self.sleep(5)

        return server


    def get_logging_instance(self, iteration):

        """ generates a logging instance (from class Logging) """

        logs = Logging(iteration = iteration, resource = self.RESOURCE, prefix = self.PREFIX, host = self.PGHOST,
        password = self.PGPASSWORD, port = self.PGPORT, shard_count = self.SHARD_COUNT)

        return logs


    def prepare_monitoring(self, iteration, server):


        """ do preperations for monitoring a run """

        # Create a logging instance
        logs = self.get_logging_instance(iteration)

        # wait to receive data from server to start monitoring
        start_monitoring = server.recv(1024)

        self.print_current_time()

        # truncate pg_log on every worker to reduce data size
        logs.prepare_monitor_run()

        # Send to server when monitoring started
        server.sendall(f"Start Monitoring".encode('UTF-8'))

        return logs


    def finish_monitoring(self, logs, server, homedir, bucket):

        """
        - stop monitoring
        - gather data
        - initiate postprocessing
        """

        # Wait for server to send ready for benchmark
        stop_monitoring = server.recv(1024)

        #### Get data from this iteration ####
        logs.stop_monitoring()

        os.chdir(homedir + "/storage")
        path = homedir + f"/logs/scripts/{self.RESOURCE}"

        # Push postgresql and IOSTAT data to blob
        run(["./push-to-blob.sh", f"{path}/pglogs/", bucket, f"{self.RESOURCE}/pglogs"], shell = False)
        run(["./push-to-blob.sh", f"{path}/general/", bucket, f"{self.RESOURCE}/general"], shell = False)

        # Wait for server to benchmark to be finished on driver
        server.sendall(f"Monitoring Finished".encode('UTF-8'))

        return "Iteration {iteration} finished"


    def monitor_iteration(self, server, homedir, bucket):

        """ for every iteration, start monitoring """

        iterations = int(self.ITERATIONS)

        for iteration in range(iterations):

                logs = self.prepare_monitoring(iteration, server)
                print(self.finish_monitoring(logs, server, homedir, bucket))


def collect_data(bucket):

    """ collect resulting data after all runs are finished """

    run(['python3', 'collect_data.py', bucket], shell = False)

