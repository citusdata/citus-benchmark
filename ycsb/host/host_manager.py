# HOST MANAGER (LOCAL DRIVER):
# If benchmark is running, i.e. if run.start on driver then start iostat on worker nodes in tmux session cpu-usage
# Wait for benchmarks to be finished
# If benchmark finished, kill tmux sessions and remove resource metrics
# Start collecting data from driver and worker nodes

import os
import sys
import time
from client import Client, collect_data


if __name__ == "__main__":

    homedir = os.getcwd()
    bucket = sys.argv[1]

    client = Client('config.yml')
    _socket = client.try_to_connect_with_socket()

    # Wait to connect with socket
    time.sleep(90)

    # monitor iterations
    client.monitor_iteration(_socket, homedir, bucket)

    # Collect data after iterations are finised
    os.chdir(homedir)
    collect_data(bucket)

    print("SUCCES: EXECUTION FINISHED")
