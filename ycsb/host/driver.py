# DRIVER SCRIPT:
# If benchmark is running, i.e. if run.start on driver then start iostat on worker nodes in tmux session cpu-usage
# Wait for benchmarks to be finished ('run.finished')
# If benchmark finished, kill tmux session cpu-usage
# Start collecting data from driver and worker nodes

import os
import pandas as pd
from helper import *
import yaml
from logs import Logging
import time
import sys

homedir = os.getcwd()
bucket = sys.argv[1]
counter = 0

# read config file
with open('config.yml', 'r') as f:
    try:
        config = yaml.safe_load(f)
        ycsb = config['ycsb']
        cluster = config['cluster']
    except yaml.YAMLError as exc:
        print(exc)


# Checks every 10 seconds if run.start on drivervm after driver is ready
time.sleep(120)

# for every iteration, start monitoring
for iteration in range(int(ycsb['iterations'])):

    print(f"Starting monitoring for iteration {iteration}")

    # Create a logging instance
    logs = Logging(iteration = iteration, resource = cluster['resource'], prefix = cluster['prefix'], host = cluster['host'], password = cluster['pgpassword'], port = cluster['port'],
    shard_count = ycsb['shard_count'])

    os.chdir(homedir + '/logs/scripts/')
    run(["./try-sign.sh", cluster['resource'], f'run.start-{iteration}', '10'], shell = False)
    os.chdir(homedir)

    # truncate pg_log on every worker to reduce data size
    logs.truncate_pg_log()

    # If run.start is found, then start monitoring on worker nodes (IOSTAT ON WORKER NODES)
    logs.start_iostat()

    print("Benchmark running on VM...")
    os.chdir(homedir + '/logs/scripts/')

    # If 'run.finished' then get all generated csv's from driver vm and store in db's
    run(["./try-sign.sh", cluster['resource'], f'run.finished-{iteration}', '30'], shell = False)

    # If run is finished, kill tmux session where iostat runs on the worker nodes
    try:
        logs.kill_tmux_session()
    except:
        ("No tmux session 'cpu-usage' running")

    # Data collection
    os.chdir(homedir)

    # Collects IOSTAT, PG_LOG data per iteration and truncates such that files are smaller
    run(['python3', 'collect_data_per_iteration.py', bucket, str(iteration)], shell = False)

# collect data per iteration?
run(['python3', 'collect_data.py', bucket], shell = False)



