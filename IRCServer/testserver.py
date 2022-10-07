import socket
import os
from webbrowser import open_new
from _thread import *


HOST = "127.0.0.1"
PORT = 4443
ThreadCount = 0

# Open Server for Connection
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen()
print(f"Listening on {PORT}")

# Allow multi-client connection ripped from https://www.positronx.io/create-socket-server-with-multiple-clients-in-python/


def multi_threaded_client(connection):
    #connection.send(str.encode('Server is working:'))
    while True:
        data = connection.recv(2048)
        #response = 'Server message: ' + data.decode('utf-8')
        # sends message to client
        response = data.decode('utf-8')
        # prints to server (can be configured as a log?)
        print(data.decode('utf-8'))
        if not data:
            break
        connection.sendall(str.encode(response))
    connection.close()


while True:
    conn, addr = s.accept()
    print(f"Connected by {addr}")
    start_new_thread(multi_threaded_client, (conn, ))
    ThreadCount += 1
    print('Thread Number' + str(ThreadCount))
    data = conn.recv(1024)
    if not data:
        break
    print(data.decode('utf-8'))
s.close()

# while True:
#     data = conn.recv(1024)
#     if not data:
#         break
#     conn.sendall(data)  # sends data back to user (echo)
#     print(data.decode('utf-8'))
