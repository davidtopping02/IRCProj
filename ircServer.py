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
import time


# Internet Relay Server class that contains the basic functionallity
class IRCServer:
    def __init__(self, hostPort, hostIP, connectedClients):
        self.hostPort = hostPort
        self.hostIP = hostIP
        self.connectedClients = connectedClients
        self.clientList = []
        self.channelList = []
        # self.rawLog = rawLog

    # command function to execute and proccess the user response
    def command(self, response, user):
        processedMessage = response.split(" ")
        key = processedMessage[0]
        # print(processedMessage)

        # if key is join, join channel
        if key == 'JOIN':

            stripper = processedMessage[1].strip("\r")
            # cycle through all channels
            for channel in self.channelList:
                if stripper == channel.channelName:

                    channel.joinChannel(channel, user)
                    print("Successfully joined: " + channel.channelName)
                    msg = f":{user.nickName}!blank@{user.clientIP} JOIN {channel.channelName}\r\n"
                    user.server_send(msg)
                else:
                    newChannel = Channel(stripper)
                    self.channelList.append(newChannel)

                    channel.joinChannel(newChannel, user)
                    print("Successfully joined: " + channel.channelName)
                    msg = f":{user.nickName}!blank@{user.clientIP} JOIN {newChannel.channelName}\r\n"
                    user.server_send(msg)

# printting all channels in the list
            print("Channels: ")
            for channel in self.channelList:
                print(channel.channelName)

        # if key is part, leave channel
        if key == 'PART':
            stripper = processedMessage[1].strip("\r")
            for channel in self.channelList:
                if (stripper == channel.channelName):

                    msg = f":{user.nickName}!@{user.clientIP} PART {channel.channelName}\r\n"
                    user.server_send(msg)
                    channel.leaveChannel(channel, user)
                    if len(channel.channelClients) == 0:
                        print("Removing channel")
                        self.channelList.remove(channel)
                    print("Successfully disconnected")
            else:
                # TODO not for mid term submission
                # channel = leaveChannel(processedMessage, user)
                print("Channel does not exist, please try again")

            print("Channels: ")
            for channel in self.channelList:
                print(channel.channelName)

        if key == 'MODE':
            stripper = processedMessage[1].strip("\r")
            for channel in self.channelList:
                if stripper == channel.channelName:

                    user.server_send(f": 324 {user.nickName} {stripper} +\r\n")
                    user.server_send(
                        f": 331 {user.nickName} {stripper} :No channel topic for this channel.\r\n")
                    for u in channel.channelClients:
                        user.server_send(
                            f": 353 {user.nickName} = {stripper} :{u.nickName}\r\n")
                    user.server_send(
                        f": 366 {user.nickName} {stripper} :End of NAMES list\r\n")

        # if key is nick, set nickname
        if key == 'NICK':

            user.set_nick(processedMessage[1])
            if user.nickName == processedMessage[1]:
                print("Your new Nickname is: " + user.nickName)

        # if key is USER, set fields of Client
        if key == 'USER':
            user.userName = (processedMessage[1])
            user.realName = processedMessage[4].replace(':', '')
            print('Your username: ' + user.userName)
            print('Your realname: ' + user.realName)
        if key == 'PRIVMSG':
            print('private message')
            # sendPriv()
        if key == 'WHO':
            stripper = processedMessage[1].strip("\r")
            for channel in self.channelList:
                if stripper == channel.channelName:

                    for u in channel.channelClients:
                        msg = (
                            f": 352 {user.nickName} {channel.channelName} tested {user.clientIP} {u.nickName} H:0 Preslav\r\n")
                        user.server_send(msg)
                    msg2 = (
                        f": 315 {user.nickName} {channel.channelName} :End of WHO List\r\n")
                    user.server_send(msg2)
        if key == 'PING':
            user.send(bytes(msg2.encode('utf-8')))
            print('ping')
        else:
            print(response)

    # Function to start the server
    def startServer(self):

        # makes new socket
        s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

        # binds socket to ip
        s.bind((self.hostIP, self.hostPort))
        s.listen()
        print(f"Server Listening on {self.hostPort}")

        testChannel = Channel("#test")
        self.channelList.append(testChannel)

        while True:
            # client is connected by address
            conn, addr = s.accept()
            print(f"Connected by {addr}")
            self.connectedClients += 1

            self.sendserver = ("Welcome User: ")
            # makes new thread for client
            start_new_thread(self.multi_threaded_client,
                             (conn, self.connectedClients))

            # Adding client to client list
            client = Client(addr[1], addr[0], conn)
            self.clientList.append(client)
            # print(self.clientList)
            print('Clients Connected : ' + str(self.connectedClients))
            data = conn.recv(1024).decode('UTF-8')
            data2 = data.split("\n")
            if not data:
                break

            # prints and calls every line seperately
            # for x in range(len(data2)):
            #     print(data2[x])
            #     self.command(data2[x], client)

        s.close()

    # Allows for multi-client connection, adapted from https://www.positronx.io/create-socket-server-with-multiple-clients-in-python/

    def multi_threaded_client(self, connection, threadNum):

        for client in self.clientList:
            client.check_connection()

        while True:
            # recieves data
            data = connection.recv(2048)
            # response = 'Server message: ' + data.decode('utf-8')
            # sends message to client
            response = data.decode('ascii')
            response2 = response.split("\n")

            # prints and calls every line seperately
            for x in range(len(response[2])):
                print(response2[x])
                self.command(response2[x], self.clientList[threadNum-1])

            if not data:
                break

            # SENDING DATA BACK DOWN
            # for clients in self.clientDetails:
            #     clients.send(str.encode(response))
        connection.close()


# Created whenever a client joins the IRC server
class Client:
    def __init__(self, port, clientIP, conn):
        self.nickName = "test"
        self.realName = ""
        self.userName = ""
        self.port = port
        self.clientIP = clientIP
        self.conn = conn
        self.connectedChannels = []
        self.startTime = time.time()  # time the client first connected
        self.sentPing = False  # check if ping has been sent
        self.gotPong = False

    # used for testing new instances of client
    # def test(self):
     #   print(self.port)
      #  print(self.clientIP)
       # print(self.nickName)

    def set_nick(self, nick):
        self.nickName = nick

    def check_connection(self):
        currentTime = time.time()
        if self.startTime + 60 < currentTime and self.sentPing is False:
            # TODO We need to add a server name
            message = ("PING TESTNET\r\n")
            self.server_send(message)
            self.sentPing = True
        if self.startTime + 120 < currentTime and self.gotPong is False:
            self.disconnect()

    def server_send(self, command):
        # TODO EVERY SERVER MESSAGE IS SENT USING FIRST USER TO CONNECT... CHANGE THIS TO ALLOW MULTI-CLIENT CHANNEL CONNECTION
        self.conn.send(bytes(command.encode()))

    def disconnect(self):
        self.conn.close()

# Created when a channel is created for the IRC


class Channel:
    def __init__(self, channelName):

        # self.serverConnection = serverConnection
        self.channelName = channelName
        self.channelClients = []
        # self.channelTopic = channelTopic

    # join Channel function, currently under development
    def joinChannel(self, channel, client):
        self.channelClients.append(client)
        for i in range(len(self.channelClients)):
            print("YO Client Name" + self.channelClients[i].nickName)

    # leave Channel funciton, under development
    def leaveChannel(self, channel, client):
        self.channelClients.remove(client)


# Creating server instance
def startServer():
    server = IRCServer(6667, "::1", 0)
    #server = IRCServer(6667, "fc00:1337::17", 0)
    server.startServer()


# this is a work around to use the channel module from this file
if __name__ == "__main__":
    startServer()
