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
import yaml
from logs import Logging
import time
import sys

homedir = os.getcwd()
bucket = sys.argv[1]

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

# # Get csv's from driver # # Get raw ycsb-data from driver for every resource group and push to blob
logs.get_csv_and_ycbs_logs()

# # Runs script that pushes gathered data to Blob storage and a PostgreSQL DB
# # Push to postgresql
os.chdir(homedir + "/storage")
path = homedir + f"/logs/scripts/{cluster['resource']}"

run(["python3", 'push_to_db.py', path, "YCSB"], shell = False)

# # Push to blob
run(["./push-to-blob.sh", f"{path}/YCSB/raw/", bucket, f"{cluster['resource']}/raw/"], shell = False)

# DELETE RESOURCE GROUP FOLDER
run(["rm", "-r", path], shell = False)
print("FOLDER REMOVED")
# DELETE RESOURCE GROUP
# os.chdir("")
# run(["rm", "-r", path], shell = False)

print("DONE")



