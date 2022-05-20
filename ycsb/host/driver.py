# DRIVER FILE:
# Waiting for driver: Checks every 10 seconds for a run.start file on driverVM
# If run.start, starts background process worker node that runs iostat
# collect these logs (nohup.out) every x seconds
# Waiting for Driver: Checks every 60 seconds for a run.finished file on driverVM
# If run.finalized, collect csv’s from driver(s) and raw YCSB output for every workload
# Collects postgresql logs from /dat/14/data/pg_log/ produced by user ‘monitor’ on every worker/coordinator
# Stores all collected files in RDS and S3 so that they persist
# If succeeded, delete locally generated files and folders


import os
import pandas as pd
from helper import *
# from run-benchmark import Benchmark
import yaml
from logs import Logging

homedir = os.getcwd()

# read config file
with open('config.yml', 'r') as f:
    try:
        config = yaml.safe_load(f)
        ycsb = config['ycsb']
        cluster = config['cluster']
    except yaml.YAMLError as exc:
        print(exc)

# Create a logging instance
logs = Logging(resource = cluster['resource'], prefix = cluster['prefix'], host = cluster['host'], password = cluster['pgpassword'], port = cluster['port'], shard_count = ycsb['shard_count'])


# after cluster is initiated
# or initiate cluster yourself in the driver file?

# Checks every 10 seconds if run.start on drivervm after driver is ready
# Ignore the authentication
os.chdir(homedir + '/logs/scripts/')
run(["./try-sign.sh", cluster['resource'], 'run.start', '10'], shell = False)
os.chdir(homedir)
print("Starting monitoring")

# # If run.start is found, then start monitoring on worker nodes
# logs.start()

os.chdir(homedir + '/logs/scripts/')
# # # If 'run.finished' then get all generated csv's from driver vm and store in db's
run(["./try-sign.sh", cluster['resource'], 'run.finished', '60'], shell = False)
os.chdir(homedir)
print("Finish monitoring")

# # # Get csv's from driver
# logs.get_csv()

# # Get raw ycsb-data from driver for every resource group?
logs.get_raw_ycsb()

# # Get raw postgresql data from worker nodes
# logs.get_postgresl()

# # Runs script that pushes gathered data to Blob storage and a PostgreSQL DB

# # Push to postgresql
# # run(["python3", 'push_to_db.py'], shell = False)

# # # Push to blob
# # run(["./push-to-s3.sh", cluster['resource']], shell = False)



