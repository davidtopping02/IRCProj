import socket
import os
import sys
from webbrowser import open_new
from _thread import *


class IRCServer:
    def __init__(self, hostPort, hostIP, connectedClients):
        self.hostPort = hostPort
        self.hostIP = hostIP
        self.connectedClients = connectedClients
        self.clientList = []
        self.channelList = []
        # self.rawLog = rawLog

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
            # Adding client to client list
            client = Client(addr[1], addr[0])
            self.clientList.append(client)
            for i in range(len(self.clientList)):
                self.clientList[i].test()

            # self.clientList[1].test()
            print('Clients Connected : ' + str(self.connectedClients))
            data = conn.recv(1024)
            if not data:
                break
            print(data.decode('UTF-8'))
            # print(b'data')

            # if ("JOIN" in data.decode('utf-8')):
            #     test = Channel("test", "test", "test")
            #     test.join()

        s.close()
    # Allows for multi-client connection, taken from https://www.positronx.io/create-socket-server-with-multiple-clients-in-python/

    def multi_threaded_client(self, connection):
        # connection.send(str.encode('Server is working:'))
        while True:
            data = connection.recv(2000)
            # response = 'Server message: ' + data.decode('utf-8')
            # sends message to client
            response = data.decode('ascii')
            # prints to server (can be configured as a log?)
            print(response)

            if not data:
                break
            connection.sendall(str.encode(response))
        connection.close()

        # Ping function to check if Clients are connected

        def send_ping():
            connection.send("PING".encode())


class Client:
    def __init__(self, port, clientIP,):
        self.nickName = b""
        self.realName = b""
        self.user = b""
        self.port = port
        self.clientIP = clientIP
        self.connectedChannels = []

    def test(self):
        print(self.port)
        print(self.clientIP)


class Channel:
    def __init__(self, channelName, channelClients, channelTopic, server="Server"):
        self.server = server
        self.channelName = channelName
        self.channelClients = channelClients
        self.channelTopic = channelTopic

    def join():
        print("joined channel")


# Creating server instance
def startServer():
    server = IRCServer(4443, "127.0.0.1", 0)
    server.startServer()


startServer()
