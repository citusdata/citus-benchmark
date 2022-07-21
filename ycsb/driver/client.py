
from helper import *
import time
import socket
import pickle

IP ="127.0.0.1"
port =  1234

def create_socket():

    """ creates socket """

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

    return server


def connect_to_socket(server):

    """ try to connect to socket and wait for message from socket """

    server.connect((IP, int(port)))
    data_len = len(server.recv(10))

    if len(data_len) > 0:
        state = sum(data_len)

    if state == 1: pass

    if state == 3: pass



def try_to_connect_with_socket():

    """
    Connect with socket
    Retries until connection can be established
    """

    server = create_socket()

    while True:

        print("trying to connect")

        try:
            connect_to_socket(server)
            return server

        except:
            time.sleep(1)


if __name__ == "__main__":

    server = try_to_connect_with_socket()

    server.send(bytearray(1))
    time.sleep(5)
    server.send(bytearray(2))
    time.sleep(5)
    server.send(bytearray(3))
    time.sleep(5)
    server.send(bytearray(4))
    time.sleep(5)
    server.send(bytearray(5))
