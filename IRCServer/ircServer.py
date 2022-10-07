import socket
import os
from webbrowser import open_new
from _thread import *

class IRCServer:
    def __init__(self, hostPort, hostIP, connectedClients):
        self.hostPort = hostPort
        self.hostIP = hostIP
        self.connectedClients = connectedClients
        self.clientList = []
        self.channelList= []
        #self.rawLog = rawLog

    #command function to execute and proccess the user response
    def command(self, response, user):
        processedMessage = response.split(" ")
        key = processedMessage[0]

        if key == 'JOIN':
            print('joining')
            if (processedMessage[1] not in self.channelList):
                channel = Channel(processedMessage[1])
                self.channelList.append(channel.channelName)


                channel.joinChannel(channel, user)
                print("Successfully joined: " + channel.channelName)

        if key == 'PART':
            print('quit')
            if (processedMessage[1] not in self.channelList):
                print("invalid channel, please try again")
            else:
                leaveChannel(processedMessage, user)
                print("Successfully disconnected")
        if key == 'MODE':
            print('mode')
        if key == 'NICK':
            user.set_nick(processedMessage[1])
            if user.nickName == processedMessage[1]:
                print("Your new Nickname is: " + user.nickName)
        if key == 'USER':
            print('user')
            #user.set_nick(processedMessage[1])
            #actualName = processedMessage[4]:1
        if key == 'PRIVMSG':
            print('private message')
                #sendPriv()
        if key == 'WHO':
            print('who')
        if key == 'PING':
            print('ping')
        else:
            print(response)

    # Function to start the server
    def startServer(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.hostIP, self.hostPort))
        s.listen()
        print(f"Server Listening on {self.hostPort}")

        while True:
            conn, addr = s.accept()
            print(f"Connected by {addr}")
            self.connectedClients += 1
            start_new_thread(self.multi_threaded_client, (conn, self.connectedClients))

            # Adding client to client list
            client = Client(addr[1], addr[0])
            self.clientList.append(client)

            # Printing entire client list
            for i in range(len(self.clientList)):
                self.clientList[i].test()

            # self.clientList[1].test()
            print('Clients Connected : ' + str(self.connectedClients))
            data = conn.recv(1024).decode('UTF-8')
            if not data:
                break

            #channel = Channel("#default")
            #self.channelList.append(channel.channelName)


            #channel.joinChannel(channel, client)
            #channel.leaveChannel(channel, client)

            print(data)
            #self.command(data, client)

            #testing for NICK
            #dataArr= data.split(" ")
            #if dataArr[0] == "NICK":
                #self.clientList[0].set_nick("poop")
                #print("new nick: " + self.clientList[0].nickName)

            
    
        s.close()
    # Allows for multi-client connection, taken from https://www.positronx.io/create-socket-server-with-multiple-clients-in-python/
    def multi_threaded_client(self, connection,threadNum):
        #connection.send(str.encode('Server is working:'))
        while True:
            data = connection.recv(2048)
            #response = 'Server message: ' + data.decode('utf-8')
            # sends message to client
            response = data.decode('ascii')
           
            print("Multi: " + response)

            self.command(response, self.clientList[threadNum-1])
            if not data:
                break
            connection.sendall(str.encode(response))
        connection.close()


class Client:
    def __init__(self, port, clientIP,):
        self.nickName = "test"
        self.realName = ""
        self.user = ""
        self.port = port
        self.clientIP = clientIP
        self.connectedChannels = []

    def test(self):
        print(self.port)
        print(self.clientIP)
        print(self.nickName)

    def set_nick(self, nick):
        self.nickName = nick


class Channel:
    def __init__(self, channelName):
        
        #self.serverConnection = serverConnection
        self.channelName = channelName
        self.channelClients = []
        #self.channelTopic = channelTopic

    def joinChannel(self, channel, client):
        self.channelClients.append(client)
        for i in range(len(self.channelClients)):
            print("YO Client Name" + self.channelClients[i].nickName)

    def leaveChannel(self, channel, client):
        print('leaving the channel')
        





# Creating server instance
def startServer():
    server = IRCServer(4443, "127.0.0.1", 0)
    server.startServer()


startServer()
