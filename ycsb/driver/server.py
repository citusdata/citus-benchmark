import socket
import time
from os.path import exists
import os
from helper import run

HOST = socket.gethostbyname(socket.gethostname())
PORT = os.getenv["SERVERPOST"]

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(3)

    clientsocket, address = s.accept()

    with clientsocket:

        print(f"Connection from {address} has been established")

        while True:
            flag = False

            while not flag:
                flag = exists("benchmark.start")
                time.sleep(1)

            # Send prepare to prepare for monitor run
            clientsocket.sendall(b"PREPARE")

            # wait until a READY from the client
            data = clientsocket.recv(1024)
            run(['touch', 'benchmark.ready'], shell = False)

            if not data:
                break

            clientsocket.sendall(b"Starting Benchmark Execution on Driver VM")
            os.remove("benchmark.start")

            flag = False

            while not flag:
                flag = exists("benchmark.finished")
                time.sleep(1)

            os.remove("benchmark.finished")
            flag = False

            clientsocket.sendall(b"Benchmark execution finished on Driver VM")
