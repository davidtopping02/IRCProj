# -----------------------------------------------------------
# Creates a bot acting as a client for an Internet Relay Chat server
#
# (C) David Topping
# https://github.com/davidtopping02/IRCProj
# -----------------------------------------------------------

# imports
from multiprocessing import connection
from time import sleep
import socket
from urllib import response
from ircServer import Channel


class BotClient:

    def __init__(self, user, nickName, channel, server, port):

        # init object attributes
        self.userName = user
        self.nickName = nickName
        self.server = server
        self.port = port
        self.serverName = ""
        self.channel = Channel(channel)

        # create socket object to gain access to the server
        self.netSocket = socket.socket()

    # Joins an IRC server from IP address and port, returns false if the connection was unsuccessful
    def connectToServer(self):
        try:
            # connect to server
            self.netSocket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            self.netSocket.connect((self.server, self.port))

            # initial joining server sequence
            self.user(self.userName)
            self.nick(self.nickName)
            self.responseHandler(True)

            self.join(self.channel.channelName)
            return True

        except socket.error:
            # cannot connect to the server
            return False

    # handles all responses recieved by the server
    def responseHandler(self, newConnection, line=None):

        # getting server name if new connection
        if newConnection == True:
            response = (self.getResponse()).split('\r\n')
            self.serverName = response[0].split(' ')[0][1:]

            for line in response:
                self.responseHandler(False, line)

        # handling each line of the resonse
        if line != '':
            # TODO TEMPORTARY TRY-CATCH TILL WE FIGURE OUT THE FORMAT OF OTHER TYPES OF MESSAGES
            try:
                # getting response code
                responseCode = line.split(self.serverName + ' ')[1][0:3]

                # RPL_NAMREPLY
                if responseCode == '353':
                   # updating the channel users
                    self.channelUsers = ((line.split(self.currentChannel + " :"))
                                         [1]).split(" ")

                else:
                    # TODO print to log file as well
                    print('<<' + line)
                    # takes out response codees
                    # print('<<' + line.split(' :')[1])
                return True
            except:
                return False

    # wrapper function to send a command along with arguments to the irc server
    def sendCMD(self, cmd, args):
        try:
            # sends the commands with args to the server
            self.netSocket.send((cmd + " " + args + "\r\n").encode())

            # prints the command with args as well
            print(">>" + cmd + " " + args)
        except:
            print("Message could not be sent, please try again")

    # revieves any messages from the server
    def getResponse(self):
        try:
            return self.netSocket.recv(2000).decode("ascii")
        except:
            return "Error recieving data from the server"

    # joins a channel
    def join(self, newChan=None):
        self.currentChannel = newChan
        self.sendCMD("JOIN", newChan)

    # TODO leave a server with an optional leaving message
    def quit(self, message):
        pass

    # changes nickname
    def nick(self, newNick=None):
        self.nickName = newNick
        self.sendCMD("NICK", self.nickName)

    # sets the user name
    def user(self, user=None):
        self.userName = user
        self.sendCMD("USER", self.nickName + "1 " + self.nickName +
                     "2 " + self.nickName + "3 " + self.userName)

    # shows the nicks of all users on channel parameter
    def names(self):
        self.sendCMD("NAMES", self.channel.channelName)

    # sends a private message to a user
    def privMsg(self, nickName, message):
        self.sendCMD("PRIVMSG", nickName + " " + message)

    # pong function replies to the ping from server
    def pongReply(self):
        self.sendCMD("PONG", "reply")

    # parses a multiline server response and returns the desired line based on input code
    def parseRecieveMessage(self, recievedMessage, code):
        recievedMessage = recievedMessage.split("\n")

        # loop through each line in the list
        for x in recievedMessage:

            # return if code hit is true
            if x.find(code) > 0:
                return x

        return -1

    # running proccess of the bot
    def runBot(self):

        # get response as list
        response = (self.getResponse()).split('\r\n')

        if response != ['']:
            for line in response:

                if self.responseHandler(False, line):
                    continue
                else:
                    # ping recieved
                    if "PING" in line:
                        self.pongReply()
                        return True

            return True
        else:
            return False


# IPv6
bot = BotClient("thisIsARealPerson", "realHuman",
                "#test", "fc00:1337::17", 6667)

# running bot sequence
if bot.connectToServer():

    while True:

        if bot.runBot() == False:
            print("ERROR: CONNECTION TO SERVER LOST\n")

            # 3 attempts to reconnect to the server
            for attempt in range(3):
                print("Attempt (%d), trying to reconnect to the server...\n" %
                      (attempt+1))

                # delay incase required for server to restart
                sleep(2)
                if bot.connectToServer() != False:
                    break
                elif attempt >= 2:
                    print('AFTER 3 ATTEMPTS THE CONNECTION COULD NOT BE ESTABLISHED')
                    exit(1)
                else:
                    continue

        else:
            continue

else:
    print("could not connect to server")
