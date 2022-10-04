import socket
import os
from webbrowser import open_new
from _thread import *


class IRCServer:
    def __init__(self, hostPort, hostIP, connectedClients):
        self.hostPort = hostPort
        self.hostIP = hostIP
        self.connectedClients = connectedClients
        #self.rawLog = rawLog

    # Function to start the server
    def startServer(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.hostIP, self.hostPort))
        s.listen()
        print(f"Server Listening on {self.hostPort}")

        while True:
            conn, addr = s.accept()
            print(f"Connected by {addr}")
            start_new_thread(self.multi_threaded_client, (conn, ))
            self.connectedClients += 1
            print('Clients Connected : ' + str(self.connectedClients))
            data = conn.recv(1024)
            if not data:
                break
            print(data.decode('utf-8'))

        s.close()
    # Allows for multi-client connection, taken from https://www.positronx.io/create-socket-server-with-multiple-clients-in-python/

    def multi_threaded_client(self, connection):
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


class Client:
    def __init__(self, nickName, realName, user, port, clientIP,):
        self.nickName = nickName
        self.realName = realName
        self.user = user
        self.port = port
        self.clientIP = clientIP


class Channel:
    def __init__(self, serverConnection, channelName, channelClients, channelTopic):
        self.serverConnection = serverConnection
        self.channelName = channelName
        self.channelClients = channelClients
        self.channelTopic = channelTopic


# Creating server instance
def startServer():
    server = IRCServer(4443, "127.0.0.1", 0)
    server.startServer()


startServer()
