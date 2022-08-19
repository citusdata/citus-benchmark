
import os
import socket
from _thread import *
from helper import run
import sys
import pickle
import threading


# states:
# ready to benchmark (start), prepared monitoring (prepared), finished bench finish, done collecting data (done)

states = [0, 0, 0, 0]

def flush():

    """ if all states are 1 then flush """

    global states
    states = [0, 0, 0, 0]


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


def update_state(index):

    """ updates state """

    global states

    print(f"Updating state on index {index}")
    states[index] = 1
    print(states)

    broadcast(states, conn)


def clientthread(conn, addr):

    global states
    print("New thread")

    # sends current states to client if connection has been made
    broadcast_with_pickle(conn, states)

    while True:

        message = conn.recv(1024)

        if not message:
            break

        try:

            msg = pickle.loads(message)
            _sum = sum(msg)

        except:
            print(f"Exception: {msg}")

        print(f"received states in phase: {msg}, {_sum}")
        current_sum = sum(states)

        if _sum <= current_sum:
            print(f"Sending states back")
            conn.send(pickle.dumps(states))
            continue

        if _sum > current_sum:
            states = msg
            print(f"Broadcasting states")
            broadcast_with_pickle(conn, states)
            continue

        if _sum == 4:
            flush()
            print("RESET STATES")
            broadcast_with_pickle(conn, states)
            continue

        if not is_state_valid(states, _sum):
            raise Exception(f"Invalid states encountered: {states}")

        print(f"Forwarding states")
        broadcast(msg, conn)


    print(f"Removing connection: {conn}")
    conn.close()
    remove(conn)

    global list_of_clients
    print(f"Remaining connections: {list_of_clients}")


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

"""The following function simply removes the object
from the list that was created at the beginning of
the program"""

def remove(connection):

    """ remove connection if client unconnects """

    if connection in list_of_clients:
        list_of_clients.remove(connection)


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


if __name__ == "__main__":

    IP = "0.0.0.0"
    PORT = int(os.getenv("SERVERPORT"))

    server = create_server()
    bind_and_listen(server, IP, PORT, 10)
    list_of_clients = []


    while True:

        """
        Accepts a connection request and stores two parameters,
        conn which is a socket object for that user, and addr
        which contains the IP address of the client that just
        connected
        """

        conn, addr = server.accept()

        """ Maintains a list of clients for ease of forwarding messages """
        list_of_clients.append(conn)

        # prints the address of the user that just connected
        print(addr[0] + " connected")

        # If local connection, make do work for benchmark.py
        start_new_thread(clientthread, (conn, addr))

        if not list_of_clients:
            conn.close()
            server.close()
            sys.exit("No open connections...\nClosing Server")
