
import os
import socket
from _thread import *
from helper import run

# code derived from / based on:
# https://www.geeksforgeeks.org/simple-chat-room-using-python/

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

IP = "0.0.0.0"
PORT = int(os.getenv("SERVERPORT"))

server.bind((IP, PORT))
server.listen(10)
list_of_clients = []

def clientthread(conn, addr):

    # sends a message to the client whose user object is conn
    conn.send(f"Connected to server with IP: {IP}".encode('utf-8'))

    i = 0
    while True:

            try:

                message = conn.recv(2048)

                if not message:
                    remove(conn)

                print("<" + addr[0] + "> " + message.decode('UTF-8'))

                # Calls broadcast function to send message to all
                message_to_send = message.decode('UTF-8') + " < " + addr[0] + " >"
                broadcast(message_to_send.encode('UTF-8'), conn)

                i += 1

                if i == 1000:
                    print("FATAL: ENDING SERVER")
                    run(["tmux", "kill-session", "-t", "server"], shell = False)

            except:

                continue

""" Using the below function, we broadcast the message to all
clients who's object is not the same as the one sending
the message """

def broadcast(message, connection):

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

    if connection in list_of_clients:

        list_of_clients.remove(connection)

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

conn.close()
server.close()
