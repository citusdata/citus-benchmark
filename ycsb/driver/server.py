
import os
import socket
from _thread import *
from helper import run
import sys

# code derived from / based on:
# https://www.geeksforgeeks.org/simple-chat-room-using-python/

def print_current_time():

    """ print current timestamp """

    run(["date"], shell = False)


def clientthread(conn, addr):

    # sends a message to the client whose user object is conn
    conn.send(f"Connected to server with IP: {IP}".encode('utf-8'))

    i = 0

    while True:
            try:
                message = conn.recv(2048)

                if not message:
                    remove(conn)

                print_current_time()
                print("<" + addr[0] + "> " + message.decode('UTF-8'))

                # Calls broadcast function to send message to all
                message_to_send = message.decode('UTF-8') + " < " + addr[0] + " >"
                broadcast(message_to_send.encode('UTF-8'), conn)
                i += 1

                if i == 1000:
                    sys.exit("FATAL: too much messages")

            except:
                continue

""" Using the below function, we broadcast the message to all
clients who's object is not the same as the one sending
the message """

def broadcast(message, connection):

    """ broadcast message to other connected clients """

    for clients in list_of_clients:
        if clients != connection:
            try:
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

        """Accepts a connection request and stores two parameters,
        conn which is a socket object for that user, and addr
        which contains the IP address of the client that just
        connected"""

        conn, addr = server.accept()

        """ Maintains a list of clients for ease forwarding messages """
        list_of_clients.append(conn)

        # prints the address of the user that just connected
        print(addr[0] + " connected")

        # creates and individual threads

        # If local connection, make do work for benchmark.py
        start_new_thread(clientthread, (conn,addr))

        if not list_of_clients:
            conn.close()
            server.close()
            sys.exit("No open connections...\nClosing Server")
