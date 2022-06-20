import os
import sys
import time
from client import Client, collect_data

homedir = os.getcwd()
bucket = sys.argv[1]
counter = 0

client = Client('config.yml')

# Wait for benchmark run
time.sleep(100)

# Create connection with socket
server = client.try_to_connect_with_socket()

# monitor iterations
client.monitor_iteration(server)

# Collect data after iterations are finised
os.chdir(homedir)

collect_data()

print("SUCCES: EXECUTION FINISHED")
