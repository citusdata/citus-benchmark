# DRIVER SCRIPT:
# If benchmark is running, i.e. if run.start on driver then start iostat on worker nodes in tmux session cpu-usage
# Wait for benchmarks to be finished ('run.finished')
# If benchmark finished, kill tmux session cpu-usage
# Start collecting data from driver and worker nodes

import os
from helper import *
import yaml
from logs import Logging
import time
import sys
import socket
import subprocess


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


PORT = int(server['port'])

# Make sure azure port is open
# run(['az', 'vm', 'open-port', '--resource-group', f'{cluster["resource"]}', '--name', f'{cluster["resource"]}-driver', '--port', str(PORT)], shell = False)

run(['./port.sh', cluster['resource'], server['port'] , '>/dev/null', '2>&1'], shell = False)

# get IP from created VM
IP = run(f"az deployment group show --resource-group {cluster['resource']} --name {cluster['resource']} --query properties.outputs.driverPublicIp.value --output tsv".split(),
stdout=subprocess.PIPE, shell = False).stdout
HOST = str(IP).split("'")[1][:-2]

# Make sure that we wait long enough so that all packages can be installed
# takes approximately 7 minutes
time.sleep(180)

# for every iteration, start monitoring
for iteration in range(int(ycsb['iterations'])):

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

        tries = 0
        connected = False
        # connect with server if server is running
        while not connected:
            try:
                s.connect((HOST, PORT))
                connected = True
            except:
                tries += 1
                if tries % 60 == 0:
                    print(str(tries / 60) + " minute(s) elapsed")
                time.sleep(1)

        # wait to receive data from server to start monitoring
        data = s.recv(1024)

        # Create a logging instance
        logs = Logging(iteration = iteration, resource = cluster['resource'], prefix = cluster['prefix'], host = cluster['host'], password = cluster['pgpassword'], port = cluster['port'],
        shard_count = ycsb['shard_count'])

        # truncate pg_log on every worker to reduce data size
        logs.truncate_pg_log()

        # If run.start is found, then start monitoring on worker nodes (IOSTAT ON WORKER NODES)
        logs.start_iostat()

        # Send to server when monitoring started
        s.sendall(b"READY")

        # Wait for server to send ready for benchmark
        data3 = s.recv(1024)

        print("Benchmark running on driver VM")

        # Wait for server to bench Finished
        data4 = s.recv(1024)

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
        s.sendall(b"READY")

# collect resulting data after all runs are finished
run(['python3', 'collect_data.py', bucket], shell = False)
