# -----------------------------------------------------------
# Creates an Internet Relay Chat server that multiple clients can connect to and interact with
#
# (C) Christian Zlatanov, Caleb Harmon
# https://github.com/davidtopping02/IRCProj
# -----------------------------------------------------------

# imports
import socket
import os
from webbrowser import open_new
from _thread import *


# Internet Relay Server class that contains the basic functionallity
class IRCServer:
    def __init__(self, hostPort, hostIP, connectedClients):
        self.hostPort = hostPort
        self.hostIP = hostIP
        self.connectedClients = connectedClients
        self.clientList = []
        self.channelList = []
        #self.rawLog = rawLog

    # command function to execute and proccess the user response
    def command(self, response, user):
        processedMessage = response.split(" ")
        key = processedMessage[0]
        
        #if key is join, join channel
        if key == 'JOIN':
            print('joining')
            if (processedMessage[1] not in self.channelList):
                channel = Channel(processedMessage[1])
                self.channelList.append(channel.channelName)

                channel.joinChannel(channel, user)
                print("Successfully joined: " + channel.channelName)

        #if key is part, leave channel
        if key == 'PART':
            print('quit')
            if (processedMessage[1] not in self.channelList):
                print("invalid channel, please try again")
            else:
                leaveChannel(processedMessage, user)
                print("Successfully disconnected")

        if key == 'MODE':
            print('mode')

        #if key is nick, set nickname
        if key == 'NICK':
            user.set_nick(processedMessage[1])
            if user.nickName == processedMessage[1]:
                print("Your new Nickname is: " + user.nickName)

        #if key is USER, set fields of Client
        if key == 'USER':
            user.userName = (processedMessage[1])
            user.realName = processedMessage[4].replace(':','')
            print('Your username: ' + user.userName)
            print('Your realname: ' + user.realName)
        if key == 'PRIVMSG':
            print('private message')
            # sendPriv()
        if key == 'WHO':
            print('who')
        if key == 'PING':
            print('ping')
        else:
            print(response)

    # Function to start the server
    def startServer(self):

        #makes new socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        #binds socket to ip
        s.bind((self.hostIP, self.hostPort))
        s.listen()
        print(f"Server Listening on {self.hostPort}")

        while True:
            #client is connected by address
            conn, addr = s.accept()
            print(f"Connected by {addr}")
            self.connectedClients += 1
            #makes new thread for client
            start_new_thread(self.multi_threaded_client,
                             (conn, self.connectedClients))

            # Adding client to client list
            client = Client(addr[1], addr[0])
            self.clientList.append(client)

        
            print('Clients Connected : ' + str(self.connectedClients))
            data = conn.recv(1024).decode('UTF-8')
            data2 = data.split("\n")
            if not data:
                break

            #prints and calls every line seperately
            for x in range(len(data2)):
                print("Server: " + data2[x])
                self.command(data2[x], client)

        s.close()
    # Allows for multi-client connection, taken from https://www.positronx.io/create-socket-server-with-multiple-clients-in-python/

    def multi_threaded_client(self, connection, threadNum):
        #connection.send(str.encode('Server is working:'))
        while True:
            #recieves data
            data = connection.recv(2048)
            #response = 'Server message: ' + data.decode('utf-8')
            # sends message to client
            response = data.decode('ascii')
            response2 = response.split("\n")

            #prints and calls every line seperately
            for x in range(len(response[2])):
                print("Multi" + response2[x])
                self.command(response2[x], self.clientList[threadNum-1])

            if not data:
                break
            connection.sendall(str.encode(response))
        connection.close()


# Created whenever a client joins the IRC server
class Client:
    def __init__(self, port, clientIP,):
        self.nickName = "test"
        self.realName = ""
        self.userName = ""
        self.port = port
        self.clientIP = clientIP
        self.connectedChannels = []

    # used for testing new instances of client
    #def test(self):
     #   print(self.port)
      #  print(self.clientIP)
       # print(self.nickName)

    def set_nick(self, nick):
        self.nickName = nick


# Created when a channel is created for the IRC
class Channel:
    def __init__(self, channelName):

        #self.serverConnection = serverConnection
        self.channelName = channelName
        self.channelClients = []
        #self.channelTopic = channelTopic

    #join Channel function, currently under development
    def joinChannel(self, channel, client):
        self.channelClients.append(client)
        #for i in range(len(self.channelClients)):
         #   print("YO Client Name" + self.channelClients[i].nickName)

    #leave Channel funciton, under development
    def leaveChannel(self, channel, client):
        print('leaving the channel')


# Creating server instance
def startServer():
    server = IRCServer(4443, "127.0.0.1", 0)
    server.startServer()


startServer()
