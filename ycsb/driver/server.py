import socket
import time
from os.path import exists
import os

HOST = socket.gethostbyname(socket.gethostname())
PORT = os.getenv["SERVERPORT"]

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(3)

    clientsocket, address = s.accept()

    with clientsocket:

        print(f"Connection from {address} has been established")

        while True:
            clientsocket.sendall(b"RECEIVED")

            data = clientsocket.recv(1024)

            if not data:
                break

            flag = False

            while not flag:
                flag = exists("benchmark.start")
                time.sleep(2)

            clientsocket.sendall(b"Starting Benchmark Execution on Driver VM")
            os.remove("benchmark.start")
            flag = False

            while not flag:
                flag = exists("benchmark.finished")
                time.sleep(3)

            os.remove("benchmark.finished")
            flag = False

            clientsocket.sendall(b"Benchmark execution finished on Driver VM")
