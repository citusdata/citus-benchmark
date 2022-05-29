import os
import subprocess
import fire
import sys
import pandas as pd
import time
from helper import *

class Logging(object):

    def get_worker_adresses(self):

        """ get adresses from workers in a citus cluster """

        os.chdir(f"{self.HOMEDIR}/logs/scripts")
        return os.popen(f"./worker-adresses.sh {self.HOST} {self.PORT} {self.PASSWORD} {self.USER} {self.DATABASE}").read().split('\n')[0].split(',')


    def __init__(self, resource, prefix, host, password = "postgres", port = 5432, user = "citus", database = "citus", iterations = 1, shard_count = 4):

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
        self.SHARD_COUNT = shard_count


        # Set environment variables
        os.environ['PGPASSWORD'] = self.PASSWORD
        os.environ['PGHOST'] = self.HOST
        os.environ['PGPORT'] = str(self.PORT)
        os.environ['PGUSER'] = self.USER
        os.environ['PGDATABASE'] = self.DATABASE
        os.environ['PREFIX'] = self.PREFIX
        os.environ['RESOURCE'] = self.RESOURCE
        os.environ['WORKERS'] = str(self.WORKERS)
        os.environ['ITERATIONS'] = str(self.ITERATIONS)
        os.environ['SHARD_COUNT'] = str(self.SHARD_COUNT)


    def prepare_postgresql_table(self):

            """
            Executes bash script that enters psql, truncates usertable if exists and creates
            a new empty usertable
            """

            os.chdir(f"{self.HOMEDIR}/logs/scripts")
            run(["./prepare-table-driver.sh", str(self.SHARD_COUNT), str(self.HOST), str(self.DATABASE), str(self.USER), str(self.PASSWORD)], shell = False)
            os.chdir(f"{self.HOMEDIR}/logs")
            print("Schema and distributed tables prepared")


    def collect_iostat(self):

        """ Collect iostat files from every worker and stores in resource_group/workername/general """

        for i, worker in enumerate(self.WORKERS):

            run(["scp", "-o", "UserKnownHostsFile=/dev/null", "-o", "StrictHostKeyChecking=no", f"{self.PREFIX}@{worker}:nohup.out", f"{self.RESOURCE}/general/worker-{i}.out"], shell = False)


    def connect_to_worker(self, worker, script):

        """ Connects to a worker via ssh, and runs a script """

        run(["ssh", "-o", "UserKnownHostsFile=/dev/null", "-o", "StrictHostKeyChecking=no", f"{self.PREFIX}@{worker}", script], shell = False)


    def create_output_directories(self):

        """ create output directories if not there yet """

        run(['mkdir', '-p', self.RESOURCE], shell = False)
        run(['mkdir', '-p', self.RESOURCE + "/YCSB/results"], shell = False)
        run(['mkdir', '-p', self.RESOURCE + "/YCSB/raw"], shell = False)
        run(['mkdir', '-p', self.RESOURCE + "/pglogs"], shell = False)
        run(['mkdir', '-p', self.RESOURCE + "/general"], shell = False)


    def get_csv_and_ycbs_logs(self, outdir = "results"):

        """ connects with VM and gets generated csv's """

        os.chdir(f'{self.HOMEDIR}/logs/scripts')
        run(["./get-csv-from-driver.sh", self.RESOURCE, f"{self.RESOURCE}/YCSB/results"], shell = False)
        run(["./get-ycsb-logs-from-driver.sh", self.RESOURCE, f"{self.RESOURCE}/YCSB/raw"], shell = False)
        os.chdir(f"{self.HOMEDIR}")


    def print_workers(self):

        """ prints all host of workers """

        for worker in self.get_worker_adresses():
            print(worker)


    def run_on_all_workers(self, script):

        """ runs script in all workers from citus cluster """

        for i, worker in enumerate(self.WORKERS):

            self.connect_to_worker(worker, script)


    def set_permissions(self):

        """
        Sets the following permissions for user 'monitor':
        alter user monitor set log_duration = on
        alter user monitor set log_min_messages = 'debug1'
        alter user monitor set log_statement to 'all'
        """

        os.chdir(f'{self.HOMEDIR}/logs/scripts')

        # change permissions on coordinator node
        run(["./alter-user.sh", self.PREFIX, self.HOST, ">", "/dev/null"], shell = False)

        # Also manually change on all workers
        for worker in self.WORKERS:
            run(["./alter-user-on-worker.sh", self.PREFIX, worker, ">", "/dev/null"], shell = False)

        os.chdir(f"{self.HOMEDIR}/logs")


    def get_postgresql(self):

        """ collects postgresql logs in /dat/14/data/pg_logs """

        os.chdir(f'{self.HOMEDIR}/logs/scripts')

        for worker_num, worker_host in enumerate(self.WORKERS):

            run(["./get-pglog.sh", self.PREFIX, worker_host, str(worker_num)], shell = False)

        os.chdir(f"{self.HOMEDIR}/logs")


    def start(self):

        """ starts the tmux process to automatically measure cpu usage during benchmarks """

        # Runs script on workers (IOSTAT) that collects CPU usage for every 2 seconds
        self.run_on_all_workers("tmux new -s cpu-usage -d; tmux send-keys -t cpu-usage 'nohup iostat -xmt 2 &' Enter")


    def kill_tmux_session(self):

        """ kills tmux session that writes iostat output to nohup.out """

        self.run_on_all_workers("tmux kill-session -t cpu-usage")


if __name__ == '__main__':

  fire.Fire(Logging)
