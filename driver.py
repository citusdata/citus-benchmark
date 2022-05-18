# DRIVER FILE:
# Builds config file with inputs from internal repo
# Reads config file (e.g. for DB credentials)
# Generates a file with metadata about citus cluster (driver_hardware, coord_hardware, coord_vcpu_num, coord_storage, worker_hardware, worker_vcpu_num, worker_storage, workers) and stores metadata.csv in output/{resource_group}
# Alters user permissions for second user ‘monitor’ (used for logging)
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
# import Threading
# from run-benchmark import Benchmark
import yaml
from model import Logging

homedir = os.getcwd()

# read config file
with open('config.yml', 'r') as f:
    try:
        config = yaml.safe_load(f)
        ycsb = config['ycsb']
        cluster = config['cluster']
    except yaml.YAMLError as exc:
        print(exc)

# Store metadata about the resource group (hardware used etc)
# try:
#     run(['python3', 'metadata.py'], shell = False)
# except:
#     pass
#     print("Metadata already stored")

# Create a logging instance
logs = Logging(resource = cluster['resource'], prefix = cluster['prefix'], host = cluster['host'], password = cluster['pgpassword'], port = cluster['port'])

# create output directories if they do not exist
logs.create_output_directories()

# Alter user permissions
logs.set_permissions()

# Checks every 10 seconds if run.start on drivervm
# Ignore the authenticity
os.chdir(homedir)
run(["./try-sign.sh", cluster['resource'], 'run.start', '10'], shell = False)

# If run.start is found, then start monitoring on worker nodes
logs.start()

# If 'run.finished' then get all generated csv's from driver vm and store in db's
run(["./try-sign.sh", cluster['resource'], 'run.finished', '60'], shell = False)

# Get csv's from driver
logs.get_csv()

# Get raw ycsb-data from driver for every resource group?
# to do

# Get raw postgresql data from worker nodes
# to do

# Runs script that pushes gathered data to Blob storage and a PostgreSQL DB

# Push to postgresql
run(["python3", 'push_to_db.py'], shell = False)

# Push to blob (Necessary to be configured with AWS cli by aws config)
run(["./push-to-s3.sh", cluster['resource']], shell = False)



