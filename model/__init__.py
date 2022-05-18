import os
import subprocess
import fire
import sys
import pandas as pd
import time
from helper import *

class Logging(object):


    def get_log_files(self):

        for i in range(self.ITERATIONS):
            run(['./get-ycsb-logs-from-driver.sh', self.RESOURCE, {self.RESOURCE}/general/worker-{i}], shell = False)



    def get_worker_adresses(self):

        """ get adresses from workers in a citus cluster """

        os.chdir(f'{self.HOMEDIR}/model')
        return os.popen(f"./worker-adresses.sh {self.HOST} {self.PORT} {self.PASSWORD} {self.USER} {self.DATABASE}").read().split('\n')[0].split(',')


    def __init__(self, resource, prefix, host, password = "postgres", port = 5432, user = "citus", database = "citus", iterations = 1):

        self.HOMEDIR = os.getcwd()
        self.PASSWORD = password
        self.HOST = host
        self.PORT = str(port)
        self.USER = user
        self.DATABASE = database
        self.PREFIX = prefix
        self.RESOURCE = resource
        self.WORKERS = self.get_worker_adresses()
        self.ITERATIONS = iterations

        # Set environment variables
        os.environ['PGPASSWORD'] = self.PASSWORD
        os.environ['PGHOST'] = self.HOST
        os.environ['PGPORT'] = str(self.PORT)
        os.environ['PGUSER'] = self.USER
        os.environ['PGDATABASE'] = self.DATABASE


    def collect_iostat(self):

        """ Collect iostat files from every worker and stores in resource_group/workername/general """

        for i, worker in enumerate(self.WORKERS):

            run(['mkdir', '-p', f"{self.RESOURCE}/general/worker-{i}"], shell = False)
            run(["scp", "-o", "UserKnownHostsFile=/dev/null", "-o", "StrictHostKeyChecking=no", f"{self.PREFIX}@{worker}:nohup.out", f"{self.RESOURCE}/general/worker-{i}"], shell = False)


    def connect_to_worker(self, worker, script):

        """ Connects to a worker via ssh, and runs a script """

        run(["ssh", "-o", "UserKnownHostsFile=/dev/null", "-o", "StrictHostKeyChecking=no", f"{self.PREFIX}@{worker}", script], shell = False)



    def create_output_directories(self):

        """ create output directories if not there yet """

        run(['mkdir', '-p', self.RESOURCE], shell = False)
        run(['mkdir', '-p', self.RESOURCE + "/YCSB/results"], shell = False)
        run(['mkdir', '-p', self.RESOURCE + "/YCSB/raw"], shell = False)
        run(['mkdir', '-p', self.RESOURCE + "/pglogging"], shell = False)
        run(['mkdir', '-p', self.RESOURCE + "/general"], shell = False)


    def get_csv(self, outdir = "results"):

        """ connects with VM and gets generated csv's """


        os.chdir(f'{self.HOMEDIR}/model')
        run(["./get-csv-from-driver.sh", self.RESOURCE, f"{self.RESOURCE}/YCSB/results"], shell = False)


    def get_raw_ycsb(self):

        """ connects with VM and gets raw ycsb log files """

        os.chdir(f'{self.HOMEDIR}/model')
        run(["./get-csv-from-driver.sh", self.RESOURCE, f"{self.RESOURCE}/YCSB/raw"], shell = False)


    def print_workers(self):

        """ prints all host of workers """

        for worker in self.get_worker_adresses():
            print(worker)


    def run_on_all_workers(self, script):

        """ runs script in all workers from citus cluster """

        for i, worker in enumerate(self.WORKERS):
            self.connect_to_worker(worker, i, script)


    def set_permissions(self):

        """
        Sets the following permissions for user 'monitor':
        alter user monitor set log_duration = on
        alter user monitor set log_min_messages = 'debug1'
        alter user monitor set log_statement to 'all'
        """

        os.chdir(f'{self.HOMEDIR}/model')
        run(["./alter-user.sh", self.PREFIX, self.HOST, ">", "/dev/null"], shell = False)


    def collect_postgres_logs(self, outputfolder, iterations):

        """ collects postgresql logs in /dat/14/data/pg_logs """

        for i in range(iterations):
            run(["", "outputfolder-"+str(i)], shell = False)


    def start(self):

        """ starts the process to automatically connect logs from the worker nodes """

        # Runs script on workers (IOSTAT) that collects CPU usage for every second
        self.run_on_all_workers("nohup iostat -xmt 1 &")

        # Sleeps 60 seconds so that cpu usage of 1 minutes is collected
        sleep(60)

        # Collect nohup.out
        self.collect_iostat()


if __name__ == '__main__':

  fire.Fire(Logging)
