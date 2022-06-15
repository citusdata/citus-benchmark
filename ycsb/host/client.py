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
import socket
import subprocess
import time


homedir = os.getcwd()
bucket = sys.argv[1]
counter = 0

# read config file
with open('config.yml', 'r') as f:
    try:
        config = yaml.safe_load(f)
        ycsb = config['ycsb']
        cluster = config['cluster']
        server = config['server']
    except yaml.YAMLError as exc:
        print(exc)


# get IP from created VM
IP = run(f"az deployment group show --resource-group {cluster['resource']} --name {cluster['resource']} --query properties.outputs.driverPublicIp.value --output tsv".split(),
stdout=subprocess.PIPE, shell = False).stdout

HOST = str(IP).split("'")[1][:-2]
PORT = int(server['port'])

print(f"Connecting with IP: {HOST}, PORT: {PORT}")

# Make sure that we wait long enough so that all packages can be installed
# takes approximately 8 minutes
# time.sleep(500)

# for every iteration, start monitoring
for iteration in range(int(ycsb['iterations'])):

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

        # connect with server if server is running
        flag = False

        while not flag:
            try:
                s.connect((HOST, PORT))
                flag = True
            except:
                time.sleep(5)

        print("Connection with server established")

        data = s.recv(1024)
        print(f"Starting monitoring for iteration {iteration}")

        # Create a logging instance
        logs = Logging(iteration = iteration, resource = cluster['resource'], prefix = cluster['prefix'], host = cluster['host'], password = cluster['pgpassword'], port = cluster['port'],
        shard_count = ycsb['shard_count'])

        # os.chdir(homedir + '/logs/scripts/')
        # run(["./try-sign.sh", cluster['resource'], f'run.start-{iteration}', '10'], shell = False)
        # os.chdir(homedir)

        # truncate pg_log on every worker to reduce data size
        logs.truncate_pg_log()

        # If run.start is found, then start monitoring on worker nodes (IOSTAT ON WORKER NODES)
        logs.start_iostat()

        # Send to server when monitoring started
        s.sendall(b"READY")

        # Wait for server to send ready for benchmark
        data2 = s.recv(1024)
        print("Benchmark running on driver VM")

        # Wait for server to bench Finished
        data3 = s.recv(1024)

        # os.chdir(homedir + '/logs/scripts/')

        # If 'run.finished' then get all generated csv's from driver vm and store in db's
        # run(["./try-sign.sh", cluster['resource'], f'run.finished-{iteration}', '30'], shell = False)

        # If run is finished, kill tmux session where iostat runs on the worker nodes
        try:
            logs.kill_tmux_session()
        except:
            ("No tmux session 'cpu-usage' running")

        # Data collection
        os.chdir(homedir)

        # Collects IOSTAT, PG_LOG data per iteration and truncates such that files are smaller
        run(['python3', 'collect_data_per_iteration.py', bucket, str(iteration)], shell = False)

        # send ok after all data is gathered and metrics are stopped
        # Send to server when monitoring started
        s.sendall(b"OK")

# collect data per iteration?
run(['python3', 'collect_data.py', bucket], shell = False)
