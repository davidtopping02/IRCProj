# -----------------------------------------------------------
# Creates a bot acting as a client for an Internet Relay Chat server
#
# (C) David Topping
# https://github.com/davidtopping02/IRCProj
# -----------------------------------------------------------

# imports
from time import sleep
import socket
from ircServer import Channel


class BotClient:

    def __init__(self, user, nickName, channel, server, port):

        # init object attributes
        self.userName = user
        self.nickName = nickName
        self.server = server
        self.port = port
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
            self.join(self.channel.channelName)
            return True

        except socket.error:
            # cannot connect to the server
            return False

    # Wrapper function to send a command along with arguments to the irc server
    def sendCMD(self, cmd, args):

        try:
            # sends the commands with args to the server
            self.netSocket.send((cmd + " " + args + "\r\n").encode())

            # prints the command with args as well
            print(cmd + " " + args)
        except:
            print("Message could not be sent, please try again")

    # revieves any messages from the server
    def getResponse(self):
        try:
            return self.netSocket.recv(2000).decode("ascii")
        except:
            return "Error recieving data from the server"

    # joins a sever
    def join(self, newChan=None):
        self.currentChannel = newChan
        self.sendCMD("JOIN", newChan)

        # store users currently in channel after joining
        self.names()

    # TODO leave a channel
    def part(self):
        pass

    # TODO leave a server with an optional leaving message
    def quit(self, message):
        pass

    # TODO lists all channels on the current network
    def list(self):
        pass

    # changes nickname
    def nick(self, newNick=None):
        self.nickName = newNick
        self.sendCMD("NICK", self.nickName)

    # sets the user name
    def user(self, user=None):
        self.userName = user
        self.sendCMD("USER", self.nickName + " " + self.nickName +
                     " " + self.nickName + " " + self.userName)

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

        # gets the response from the server
        recievedText = self.getResponse()
        print(recievedText)

        # error recived
        if "ERROR" in recievedText:
            return False
        # ping recieved
        elif "PING" in recievedText:
            self.pongReply()
            return True

        # 353s contains channel users
        elif "353" in recievedText:

            # full line of 353 from
            line = self.parseRecieveMessage(recievedText, "353")

            # parsing the line to and puts the current channel users in the object field
            self.channelUsers = ((line.split(self.currentChannel + " :"))
                                 [1][: - 1]).split(" ")

            # for testing
            # print(self.channelUsers)

        else:
            sleep(2)


# used for an IPv4 connection (for testing)
# init bot client object
# bot = BotClient("thisIsARealPerson", "realHuman",
#                 "#test", "10.0.42.17", 6667)

# IPv6
bot = BotClient("thisIsARealPerson", "realHuman",
                "#test", "fc00:1337::17", 6667)

# running bot sequence
if bot.connectToServer():

    while True:
        bot.runBot()
else:
    print("could not connect to server")
