
import os
import socket
from _thread import *
from helper import run
import sys
import pickle
import threading
import time
import logging

logging.basicConfig(level=logging.NOTSET)

# states:
# ready to benchmark (start), prepared monitoring (prepared), finished bench finish, done collecting data (done)

states = [0, 0, 0, 0, 0, 0]
ip = socket.gethostbyname(socket.gethostname())


def bitwise_or(a, b):

    """ returns new list of states with bitwise or operation executed """

    if len(a) != len(b):
        raise Exception(f"length of lists are not equal\na {a} ({len(a)}), b: {b} ({len(b)})")

    result = []

    for i in range(len(a)):
        result.append(a[i] + b[i] - (a[i] * b[i]))

    return result


def flush():

    """ if all states are  1 then flush """

    global states

    states = [0, 0, 0, 0, 0, 0]
    print(f"States are flushed\nNew states: {states}")


def remove(connection):

    """ remove connection if client unconnects """

    if connection in list_of_clients:

        list_of_clients.remove(connection)


""" Using the below function, we broadcast the message to all
clients who's object is not the same as the one sending
the message """

def broadcast(message, connection):

    """ broadcast message to other connected clients """

    for clients in list_of_clients:

        if clients != connection:

            try:
                print(f"forwarding to: {clients}")
                clients.sendall(message)

            except:
                clients.close()

                # if the link is broken, we remove the client
                remove(clients)


def broadcast_with_pickle(conn, message):

    """ sends pickled message to server """

    try:
        broadcast(pickle.dumps(message), conn)

    except:
        print("Sending package to server failed")


def is_state_valid(states, index):

    """ simple checksum to see if states are correct """

    return sum(states) == index


def print_current_time():

    """ print current timestamp """

    run(["date"], shell = False)


def update_state(index, conn):

    """ updates state """

    global states

    logging.debug(f"Updating state on index {index}")
    states[index] = 1
    logging.debug(states)

    broadcast(states, conn)

def set_states_to_ready():

    global states


def clientthread(conn, addr):

    global states

    # sends current states to clients if connection has been made
    for client in list_of_clients:
        client.sendall(pickle.dumps(states))

    while True:

        message = conn.recv(1024)

        if not message:
            break

        try:

            msg = pickle.loads(message)
            _sum = sum(msg)
            logging.debug(f'received states: {msg}')

        except:
            logging.warning(f"Exception: {message}")

        logging.debug(f"Received states in phase: {msg}, {_sum}")
        current_sum = sum(states)

        if current_sum == 6:
            states = [0, 0, 0, 0, 0, 0]
            states = bitwise_or(states, msg)
            broadcast_with_pickle(conn, states)
            continue

        states = bitwise_or(states, msg)
        logging.debug(f"States updated to {states}\nBroadcasting")
        broadcast_with_pickle(conn, states)

    logging.info(f"Removing connection: {conn}")
    conn.close()
    remove(conn)

    logging.info(f"Remaining connections: {list_of_clients}")


def create_server():

    """ creates a server """

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    return server


def bind_and_listen(server, ip, port, listen = 10):

    """
    - binds to a port
    - listens to incoming connections
    """

    server.bind((ip, port))
    server.listen(listen)


def keep_connections_alive(seconds = 60, msg = b'\x0a'):

    """ send heartbeat messages to keep connections alive """

    global list_of_clients
    global ip
    global states

    while True:

        if not list_of_clients:
            continue


        for client in list_of_clients:

            if client.getpeername()[0] == ip:
                continue

            logging.info(f"Sending {states} as heartbeat to {client.getpeername()[0]}")

        try:

            client.send(pickle.dumps(states))

        except Exception as e:

            logging.info(f'Exception: {e}')

        time.sleep(seconds)



if __name__ == "__main__":

    """
    Accepts a connection request and stores two parameters,
    conn which is a socket object for that user, and addr
    which contains the IP address of the client that just
    connected
    """

    list_of_clients = []

    IP = "0.0.0.0"
    PORT = int(os.getenv("SERVERPORT"))

    server = create_server()
    bind_and_listen(server, IP, PORT, 10)
    start_new_thread(keep_connections_alive, (60, b'\x0a'))

    while True:

        conn, addr = server.accept()

        """ Maintains a list of clients for ease of forwarding messages """

        list_of_clients.append(conn)

        # prints the address of the user that just connected
        logging.info(addr[0] + " connected")

        # If local connection, make do work for benchmark.py
        start_new_thread(clientthread, (conn, addr))

        if not list_of_clients:

            conn.close()
            server.close()

            sys.exit("No open connections...\nClosing Server")
