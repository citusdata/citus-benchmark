#!/bin/bash

import os
import subprocess
import fire
import sys
import pandas as pd
import time
from helper import *

class Logging(object):


    def __init__(self, resource, prefix, host, password = "postgres", port = 5432, user = "citus", database = "citus"):

        self.HOMEDIR = os.getcwd()
        self.PASSWORD = password
        self.HOST = host
        self.PORT = str(port)
        self.USER = user
        self.DATABASE = database
        self.PREFIX = prefix
        self.RESOURCE = resource

        # Set environment variables
        os.environ['PGPASSWORD'] = self.PASSWORD
        os.environ['PGHOST'] = self.HOST
        os.environ['PGPORT'] = str(self.PORT)
        os.environ['PGUSER'] = self.USER
        os.environ['PGDATABASE'] = self.DATABASE


    def get_worker_adresses(self):

        """ get adresses from workers in a citus cluster """
        
        return os.popen(f"./worker-adresses.sh {self.HOST} {self.PORT} {self.PASSWORD} {self.USER} {self.DATABASE}").read().split('\n')[0].split(',')


    def connect_to_worker(self, worker, workerName, script, outputdir = "output"):

        """ Connects to a worker via ssh, and runs a script """

        run(["ssh", "-o", "UserKnownHostsFile=/dev/null", "-o", "StrictHostKeyChecking=no", f"{self.PREFIX}@{worker}", script], shell = False)

        # copy file from remote to local
        # now it opens a new ssh to copy the file to local

        # make directory to store logging files
        run(['mkdir', '-p', outputdir], shell = False)


        run(["scp", "-r", "-o", "UserKnownHostsFile=/dev/null", "-o", "StrictHostKeyChecking=no", f"{self.PREFIX}@{worker}:results", f"{outputdir}"], shell = False)

        # sleep(10)

        # run([""])

        # get files generated on worker and store on local

        # run(["ssh", "-o", "UserKnownHostsFile=/dev/null", "-o", "StrictHostKeyChecking=no", f"{self.PREFIX}@{worker}", "'(iostat -xmt 1 > cpu.log) &'"], shell = False)

    def get_csv(self, outdir = "results"):

        # make directory to store logging files
        run(['mkdir', '-p', outdir], shell = False)
        run(['mkdir', '-p', outdir + "/YCSB"], shell = False)

        run(["./get-csv-from-driver.sh", self.RESOURCE, outdir + "/YCSB"], shell = False)
   

    def print_workers(self):

        """ prints all host of workers """

        for worker in self.get_worker_adresses():
            print(worker)


    def connect(self):

        """ runs script in all workers from citus cluster """

        # script = "iostat > cpu.log; cat cpu.log"
        script = "mkdir results; iostat > results/cpu.log; cat results/cpu.log; ps aux > results/processes.log"

        for i, worker in enumerate(self.get_worker_adresses()):
            self.connect_to_worker(worker, i, script)


    def alter_permissions(self):

        """ give user monitor all necessary permissions """
        
        run(f"./alter-user.sh {self.HOST} {self.PORT} {self.PASSWORD} {self.USER} {self.DATABASE}".split(' '))


    def set_permissions(self):

        """ this doesn't work yet as it is a shell in a shell """

        # past alter-role script in citus coordinator
        run(["scp", "-r", "-o", "UserKnownHostsFile=/dev/null", "-o", "StrictHostKeyChecking=no", f"{self.PREFIX}@{worker}:.", f"{outputdir}"], shell = False)

        # maybe add script first to coord
        # then sudo su postgres; script.sh 

        # sudo su postgres
        # psql -d citus
        # alter user monitor set log_duration to on;
        # alter user monitor set log_statement = "all";


        # Connect via SSH to coordinator node
        run(["ssh", "-o", "UserKnownHostsFile=/dev/null", "-o", "StrictHostKeyChecking=no", f"{self.PREFIX}@{self.HOST}", "sudo su postgres; pwd"], shell = False)

    
if __name__ == '__main__':

  fire.Fire(Logging)


