# -----------------------------------------------------------
# Creates an Internet Relay Chat server that multiple clients can connect to and interact with
#
# (C) Christian Zlatanov, Caleb Harmon
# https://github.com/davidtopping02/IRCProj
# -----------------------------------------------------------

# imports
from genericpath import exists
from queue import Empty
import socket
from _thread import *
import time

from grpc import server


# Internet Relay Server class that contains the basic functionallity
class IRCServer:
    def __init__(self, hostPort, hostIP, connectedClients):
        self.serverName = 'G6-IRCServer'
        self.hostPort = hostPort
        self.hostIP = hostIP
        self.connectedClients = connectedClients
        self.clientList = []
        self.channelList = []

        # creates new socket object
        self.serverSocket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

    # Starts server on specified ip and port

    def startServer(self):

        # binds socket to ip
        self.serverSocket.bind((self.hostIP, self.hostPort))
        print(f"Server Listening on {self.hostPort}")

    # listens for client
    def server_listen(self):

        # listening on port
        self.serverSocket.listen()

        # main loop for new clients (put in seperate function)
        while True:

            # client is connected by address
            conn, addr = self.serverSocket.accept()
            print('New connection' + str(addr))

            # Adding client to client list
            client = Client(addr[1], addr[0], conn)
            self.clientList.append(client)
            self.connectedClients += 1

            # makes new thread for client
            start_new_thread(self.multi_threaded_client,
                             (conn, self.connectedClients))

    # Allows for multi-client connection, adapted from https://www.positronx.io/create-socket-server-with-multiple-clients-in-python/
    def multi_threaded_client(self, connection, threadNum):

        # for client in self.connectedClients:
        #     client.check_connection()

        while True:
            # recieves data
            data = connection.recv(2048)
            response = (data.decode('ascii')).split("\n")

            # deal with client response: (response, threadNum-clientID)
            self.responseHandler(response, self.clientList[threadNum-1])

            if not data:
                break
        connection.close()

    # response handler for every line sent by client
    def responseHandler(self, response, client):

        # loops through each response line
        for line in response:

            # checking response line is not empty
            if line != '':

                print('>>'+line)

                # format- prefix:command:args
                line = line.split(' ', 1)

                if line[0] == 'PING':
                    client.server_send(
                        f":{self.serverName} PONG {self.serverName} :{line[1]}\r\n")
                    continue

                elif line[0] == 'PRIVMSG':
                    self.privHandler(line[1], client)

                elif line[0] == 'NICK':
                    self.nickHandler(client, line[1].strip('\r'))
                elif line[0] == 'USER':
                    args = line[1].split(' ')
                    # split args into username and realname
                    client.userName = args[0]
                    client.realName = args[3].replace(':', '').strip('\r')

                    # send welcome message
                    if client.nickName != '' and client.realName != '':
                        client.server_send(
                            f":{self.serverName} 002 {client.nickName} :Host - {socket.gethostname()}, Version: 2.0\r\n")
                        client.server_send(
                            f":{self.serverName} 003 {client.nickName} :Server was created as of recent\r\n")
                        client.server_send(
                            f":{self.serverName} 004 {client.nickName} {socket.gethostname()}, 2.0\r\n")
                        client.server_send(
                            f":{self.serverName} 251 {client.nickName} :Number of users on: {len(self.clientList)}\r\n")
                        client.server_send(
                            f":{self.serverName} 422 {client.nickName} :MOTD ERROR.\r\n")

                elif line[0] == 'JOIN':
                    self.joinHandler(client, line[1])

                elif line[0] == 'PART':
                    self.partHandler(client, line[1])

                elif line[0] == 'MODE':
                    stripper = line[1].strip('\r')
                    for channel in self.channelList:
                        if line[1].strip('\r') == channel.channelName:
                            pass
                            client.server_send(f": 342")
                            client.server_send(
                                f": 324 {client.nickName} {stripper} \r\n")
                            client.server_send(
                                f": 331 {client.nickName} {stripper} :No channel topic for this channel.\r\n")

                            for connectedClient in channel.channelClients:
                                client.server_send(
                                    f": 353 {client.nickName} = {stripper} :{connectedClient.nickName}\r\n")

                            client.server_send(
                                f": 366 {client.nickName} {stripper} :End of NAMES list\r\n")

                elif line[0] == 'WHO':
                    for channel in self.channelList:
                        if line[1].strip('\r') == channel.channelName:

                            for channelClient in channel.channelClients:
                                client.server_send(
                                    f": 352 {client.nickName} {channel.channelName} tested {client.clientIP} {channelClient.nickName} H:0 Preslav\r\n")

                            client.server_send(
                                f": 315 {client.nickName} {channel.channelName} :End of WHO List\r\n")

    def nickHandler(self, client, newNick):

        # storing old nick for the change of nick command
        oldNick = client.nickName

        # verifying if the nickname is repeated
        for channel in self.channelList:
            for user in channel.channelClients:

                if user.nickName == newNick:
                    # :david-VirtualBox 433 * david :Nickname is already in use\r\n
                    client.server_send(
                        f":{socket.gethostname()} 433 * {user.nickName} :Nickname is already in use\r\n")

        # sets the client's nickname
        client.nickName = newNick
        print(client.nickName)

        # sends the confirmation
        client.server_send(
            f":{oldNick}!{client.clientIP} NICK {client.nickName}\r\n")

    # handler for dealing with PRIVMSG
    def privHandler(self, args, client):

        args = args.split(' :', 1)

        # checks if our chosen channel exits in the channelList
        for channel in self.channelList:
            if args[0] == channel.channelName:

                # sends our message to all other clients in the Server
                for user in channel.channelClients:
                    if user.nickName == client.nickName:
                        continue
                    user.server_send(
                        f":{client.nickName}!{client.userName}@{socket.gethostname()} PRIVMSG {args[0]} :{args[1]}\r\n")

    # handler function for joining a channel
    def joinHandler(self, client, channelName):

        channelExists = False
        # create new channel if list is empty
        if len(self.channelList) == 0:
            # create a channel
            newChan = Channel(channelName.strip('\r'))

            # append client to new channel
            newChan.channelClients.append(client)

            # append to server channel list
            self.channelList.append(newChan)

            # joined channel message
            client.server_send(
                f":{client.nickName}!{client.realName}@{client.clientIP} JOIN {newChan.channelName}\r\n")

        #  a channel exists
        elif len(self.channelList) != 0:

            for channel in self.channelList:

                # checks if the channel to be joined already exists
                if channelName.strip('\r') == channel.channelName:
                    channel.channelClients.append(client)
                    msg = f":{client.nickName}!{client.realName}@{client.clientIP} JOIN {channel.channelName}\r\n"
                    client.server_send(msg)
                    #                 client.server_send(
                    #                     'You have successfully joined ' + channel.channelName + '! :)\r\n')
                    channelExists = True
                else:
                    pass
            if channelExists == False:
                newChannel = Channel(channelName.strip('\r'))
                newChannel.channelClients.append(client)
                self.channelList.append(newChannel)
                msg = f":{client.nickName}!{client.realName}@{client.clientIP} JOIN {newChannel.channelName}\r\n"

                client.server_send(msg)

            # handler function for joining a channel
            # def joinHandler(self, client, channelName):

            #     # create new channel if list is empty
            #     if len(self.channelList) == 0:
            #         # create a channel
            #         newChan = Channel(channelName.strip('\r'))

            #         # append client to new channel
            #         newChan.channelClients.append(client)

            #         # append to server channel list
            #         self.channelList.append(newChan)

            #         # joined channel message
            #         client.server_send(
            #             f":{client.nickName}!blank@{client.clientIP} JOIN {newChan.channelName}\r\n")

            #         client.server_send('You have successfully joined ' +
            #                            newChan.channelName + '! :)\r\n')

            #     else:
            #         # cycle through all channels
            #         for channel in self.channelList:

            #             # checking if the channel exists already
            #             if channelName.strip('\r') == channel.channelName:

            #                 channel.channelClients.append(client)
            #                 msg = f":{client.nickName}!blank@{client.clientIP} JOIN {channel.channelName}\r\n"
            #                 client.server_send(msg)
            #                 client.server_send(
            #                     'You have successfully joined ' + channel.channelName + '! :)\r\n')
            #             else:
            #                 newChannel = Channel(channelName.strip('\r'))
            #                 newChannel.channelClients.append(client)
            #                 self.channelList.append(newChannel)
            #                 msg = f":{client.nickName}!blank@{client.clientIP} JOIN {newChannel.channelName}\r\n"
            #                 client.server_send(
            #                     'You have successfully joined ' + newChannel.channelName + '! :)\r\n')
            #                 client.server_send(msg)

            # handler for part (leaving channel)

    def partHandler(self, client, channelName):

        # cycles through all channels
        for channel in self.channelList:

            for user in channel.channelClients:

                # compares channel name
                if (channelName.split(' ')[0] == channel.channelName) and (user.nickName == client.nickName):

                    # sends successful parting message
                    client.server_send(
                        f":{client.nickName}!@{client.clientIP} PART {channel.channelName}\r\n")

                    # remove client from the channel list
                    channel.channelClients.remove(client)

                    # removes the channel if there are no other users
                    if len(channel.channelClients) == 0:
                        print("Removing channel")
                        self.channelList.remove(channel)
                    print("Successfully disconnected")

                else:
                    client.server_send(
                        f":{server.serverName} 442 {client.nickName} {channelName.split(' ')[0]} :You're not on that channel\r\n")


class Client:
    def __init__(self, port, clientIP, conn):
        self.nickName = ""
        self.realName = ""
        self.userName = ""
        self.port = port
        self.clientIP = clientIP
        self.conn = conn
        self.connectedChannels = []
        self.startTime = time.time()  # time the client first connected
        self.sentPing = False  # check if ping has been sent
        self.gotPong = False

    # def check_connection(self):
    #     currentTime = time.time()
    #     if self.startTime + 60 < currentTime and self.sentPing is False:
    #         # TODO We need to add a server name
    #         message = ("PING TESTNET\r\n")
    #         self.server_send(message)
    #         self.sentPing = True
    #     if self.startTime + 120 < currentTime and self.gotPong is False:
    #         self.disconnect()

    def server_send(self, command):
        self.conn.send(bytes(command.encode()))
        print('<<' + command)

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


# this is a work around to use the channel module from this file
if __name__ == "__main__":

    # instantiate server object and starts the server main running loop
    server = IRCServer(6667, "fc00:1337::17", 0)
    server.startServer()
    server.server_listen()

    # closes port
    server.serverSocket.close()
