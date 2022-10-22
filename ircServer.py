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

        while True:

            # recieves data
            try:
                data = connection.recv(2048)
            except:
                exit()

            response = (data.decode('ascii')).split("\n")

            # deal with client response: (response, threadNum-clientID)
            self.responseHandler(response, self.clientList[threadNum-1])

            if not data:
                break
            now = time.time()

            try:
                if self.clientList[threadNum-1].lastConnectionCheck + 10 < now:
                    self.sentPing = False
                    for client in self.clientList:
                        client.gotPong = False
                        client.check_connection()
            except:
                pass

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

                # Checking if client pongs
                elif line[0] == 'PONG':
                    client.pong_handler()

                elif line[0] == 'QUIT':
                    self.quitHandler(client)

    def quitHandler(self, client):
        # handler to kick user upon quit
        try:
            client.conn.close()
        except:
            print("Error closing socket")

        # cycles through all channesl and removes user from their joined ones
        for channel in self.channelList:
            channel.channelClients.remove(client)
            if len(channel.channelClients) == 0:
                self.channelList.remove(channel)

        for user in self.clientList:
            if client.userName == user.userName:
                self.clientList.remove(client)

        self.connectedClients += -1

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

        if args[0] == "":
            user.server_send(
                f":{socket.gethostname()} 411 {client.nickName} :No recipient given (PRIVMSG)\r\n")
        if args[1] == "":
            user.server_send(
                f":{socket.gethostname()} 412 {client.nickName} :No text to send\r\n")

        # checks if our chosen channel exits in the channelList
        for channel in self.channelList:
            if args[0] == channel.channelName:

                # sends our message to all other clients in the Server
                for user in channel.channelClients:
                    if user.nickName == client.nickName:
                        continue
                    user.server_send(
                        f":{client.nickName}!{client.userName}@{socket.gethostname()} PRIVMSG {args[0]} :{args[1]}\r\n")

        # checks if user is in clientList
        for user in self.clientList:
            # if the recipient is the user we are looking for
            if args[0] == user.nickName:
                # send private message to our recipient
                user.server_send(
                    f":{client.nickName}!{client.realName}@{socket.gethostname()} PRIVMSG {args[0]} {args[1]}\r\n")
           # elif args[0] not in self.clientList:
            #    user.server_send(f":{socket.gethostname()} 401 {client.nickName} {args[0]} :No such nick/channel\r\n")

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
                    # loop for each client in a channel
                    for dude in channel.channelClients:
                        msg = f":{client.nickName}!{client.realName}@{client.clientIP} JOIN {channel.channelName}\r\n"

                        # each client sends the msg individually
                        dude.server_send(msg)
                    channelExists = True
                else:
                    pass
            # if channel does not exist
            if channelExists == False:
                # create a new channel
                newChannel = Channel(channelName.strip('\r'))
                # append user to channel list
                newChannel.channelClients.append(client)
                self.channelList.append(newChannel)
                msg = f":{client.nickName}!{client.realName}@{client.clientIP} JOIN {newChannel.channelName}\r\n"

                client.server_send(msg)

    def partHandler(self, client, channelName):

        # cycles through all channels
        for channel in self.channelList:

            for user in channel.channelClients:

                # compares channel name
                if (channelName.split(' ')[0] == channel.channelName):
                    if (user.nickName == client.nickName):

                        # sends successful parting message
                        for dude in channel.channelClients:
                            dude.server_send(
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
        self.lastConnectionCheck = time.time()

    # check for inactive clients using time library
    def check_connection(self):
        currentTime = time.time()
        if self.startTime + 60 < currentTime and self.sentPing is False:
            # self.sentPing = True
            message = (f"PING {socket.gethostname()}\r\n")
            self.server_send(message)
        elif self.startTime + 120 < currentTime and self.gotPong is False:
            self.disconnect()

    def pong_handler(self):
        self.gotPong = True
        self.startTime = time.time()  # change startTime to time of last pong reply
        self.sentPing = False  # Reset sent ping to false

    def server_send(self, command):
        self.conn.send(bytes(command.encode()))
        print('<<' + command)

    def disconnect(self):
        # TODO add a message when the server disconnects you
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
    # server = IRCServer(6667, "::1", 0)
    server.startServer()
    server.server_listen()

    # closes port
    server.serverSocket.close()
