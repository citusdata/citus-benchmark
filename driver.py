import os
import subprocess
import fire
import sys
import pandas as pd
import time
from helper import *
# import Threading
# from run-benchmark import Benchmark
import yaml
from model import Logging

homedir = os.getcwd()

# read config file which is build earlier
with open('config.yml', 'r') as f:
    try:
        config = yaml.safe_load(f)
        ycsb = config['ycsb']
        cluster = config['cluster']
    except yaml.YAMLError as exc:
        print(exc)

print(config)

# Store metadata
# run(['python3', 'metadata.py'], shell = False)

# Create a logging instance
logs = Logging(resource = cluster['resource'], prefix = cluster['prefix'], host = cluster['host'], password = cluster['pgpassword'], port = cluster['port'])

# create output directories if they do not exist
# logs.create_output_directories()

logs.get_worker_adresses()

# Alter user permissions
# logs.set_permissions()

# Checks every 10 seconds if run.start on drivervm
# run(["./try-sign.sh", 'run.start', cluster['resource'], '10'])

# If run.start is found, then start monitoring on worker nodes

# If 'run.finished' then get all generated csv's from driver vm and store in RDS and S3
# run(["./try-sign.sh", 'run.finished', '60'])

