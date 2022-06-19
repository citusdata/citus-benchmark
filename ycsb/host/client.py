# DRIVER SCRIPT:
# If benchmark is running, i.e. if run.start on driver then start iostat on worker nodes in tmux session cpu-usage
# Wait for benchmarks to be finished
# If benchmark finished, kill tmux sessions and remove resource metrics
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

# Open port from VM
PORT = int(server['port'])
run(['./port.sh', cluster['resource'], server['port'] , '>/dev/null', '2>&1'], shell = False)

# get IP from created VM
IP = run(f"az deployment group show --resource-group {cluster['resource']} --name {cluster['resource']} --query properties.outputs.driverPublicIp.value --output tsv".split(),
stdout=subprocess.PIPE, shell = False).stdout
HOST = str(IP).split("'")[1][:-2]

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Make sure that we wait long enough so that all packages can be installed
run(["date"], shell = False)
time.sleep(180)

# connect with server if server is running
while True:
    try:
        server.connect((HOST, PORT))
        break
    except:
        time.sleep(10)

# for every iteration, start monitoring
for iteration in range(int(ycsb['iterations'])):

        # wait to receive data from server to start monitoring
        start_monitoring = server.recv(1024)

        # Create a logging instance
        logs = Logging(iteration = iteration, resource = cluster['resource'], prefix = cluster['prefix'], host = cluster['host'], password = cluster['pgpassword'], port = cluster['port'],
        shard_count = ycsb['shard_count'])

        # truncate pg_log on every worker to reduce data size
        logs.truncate_pg_log()

        # If run.start is found, then start monitoring on worker nodes (IOSTAT ON WORKER NODES)
        logs.start_iostat()

        # Send to server when monitoring started
        server.sendall(f"Start Monitoring".encode('UTF-8'))

        # Wait for server to send ready for benchmark
        stop_monitoring = server.recv(1024)

        #### Get data from this iteration ####

        # Collect cpu usage from worker nodes
        logs.collect_iostat()

        #  Delete nohup.out generated by iostat
        logs.delete_iostat()

        #  Get raw postgresql data from worker nodes
        logs.get_postgresql()

        os.chdir(homedir + "/storage")
        path = homedir + f"/logs/scripts/{cluster['resource']}"

        # Push postgresql and IOSTAT data to blob
        run(["./push-to-blob.sh", f"{path}/pglogs/", bucket, f"{cluster['resource']}/pglogs"], shell = False)
        run(["./push-to-blob.sh", f"{path}/general/", bucket, f"{cluster['resource']}/general"], shell = False)

        # Wait for server to benchmark to be finished on driver
        server.sendall(f"Monitoring Finished".encode('UTF-8'))

        print(f"Iteration {iteration} finished")

os.chdir(homedir)
# collect resulting data after all runs are finished
run(['python3', 'collect_data.py', bucket], shell = False)
