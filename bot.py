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
import random
from datetime import datetime


class BotClient:

    def __init__(self, user, nickName, channel, server, port):

        # init object attributes
        self.userName = user
        self.nickName = nickName
        self.server = server
        self.port = port
        self.serverName = ''
        self.channel = Channel(channel)

        # load in bot facts file
        with open('botFacts.txt', encoding='utf8') as f:
            self.botFacts = [line.rstrip('\n') for line in f]

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

            # response handler incase the nick name is already taken
            self.responseHandler((self.getResponse()).split('\r\n')[:-1])
            self.join(self.channel.channelName)

            return True

        except socket.error:
            # cannot connect to the server
            return False

    # wrapper function to send a command along with arguments to the irc server
    def sendCMD(self, cmd, args):
        try:
            # sends the commands with args to the server
            self.netSocket.send((cmd + ' ' + args + '\r\n').encode())

            # prints the command with args as well
            print('<<' + cmd + ' ' + args)
        except:
            print('Message could not be sent, please try again')

    # revieves any messages from the server
    def getResponse(self):
        try:
            return self.netSocket.recv(2000).decode('ascii')
        except:
            return 'Error recieving data from the server'

    # joins a channel
    def join(self, newChan=None):
        self.channel.channelName = newChan
        self.sendCMD('JOIN', newChan)

        pass

    # changes nickname
    def nick(self, newNick=None):

        # sends the NICK command
        self.nickName = newNick
        self.sendCMD('NICK', self.nickName)

    # sets the user name
    def user(self, user=None):
        self.userName = user
        self.sendCMD('USER', self.nickName + '1 ' + self.nickName +
                     '2 ' + self.nickName + '3 ' + self.userName)

    # sends a private message to a user
    def privMsg(self, target, message):
        self.sendCMD('PRIVMSG', target + ' :' + message)

    # pong function replies to the ping from server
    def pongReply(self):
        self.sendCMD('PONG', self.nickName)

    # parses a multiline server response and returns the desired line based on input code
    def parseRecieveMessage(self, recievedMessage, code):
        recievedMessage = recievedMessage.split('\n')

        # loop through each line in the list
        for x in recievedMessage:

            # return if code hit is true
            if x.find(code) > 0:
                return x

        return -1

    # deals with all responses from the server
    def responseHandler(self, response):

        for line in response:
            print('>>'+line)

            # dealing with ping
            if line.startswith('PING'):
                self.pongReply()

            # ensuring line has prefix
            if line[0] == ':':

                try:
                    # format- prefix:command:args
                    line = line.split(' ', 2)

                    # set channel topic
                    if line[1] == '331':
                        pass
                    elif line[1] == '353':
                        self.namesHandler(line[2])
                    elif line[1] == '433':
                        self.repeatedNickHandler()
                    elif line[1] == 'JOIN':
                        self.JOINHandler(line[0], line[2])
                    elif line[1] == 'QUIT':
                        self.QUITHandler(line[0])
                    elif line[1] == 'NICK':
                        self.nickHandler(line[0], line[2])
                    elif line[2] == self.channel.channelName + ' :!hello':
                        self.helloHandler()
                    elif line[2] == self.channel.channelName + ' :!slap':
                        self.slapHandler()
                    elif line[1] == 'PRIVMSG':
                        self.privMsgHandler(line[0], line[1], line[2])
                except:
                    print('ERROR: unexpected command')

    # handler for the 353 command
    def namesHandler(self, args):
        self.channel.channelClients = args.split(
            self.channel.channelName + ' :')[1].split(' ')

    # handler for 433 command
    def repeatedNickHandler(self):

        # updating nick name
        self.nickName = (self.nickName + '_')
        self.sendCMD('NICK', self.nickName)

        # update incase name taken again
        self.responseHandler((self.getResponse()).split('\r\n')[:-1])

    # handler for JOIN command
    def JOINHandler(self, prefix, args):

        # appending client to the channel list
        if args == self.channel.channelName and prefix[1:].startswith(self.nickName) == False:
            self.channel.channelClients.append(prefix[1:].split('!', 1)[0])

    # handler for QUIT command
    def QUITHandler(self, prefix):

        # getting user from prefix
        user = prefix[1:].split('!', 1)[0]

        # updating channel list
        self.channel.channelClients.remove(user)

    # handler for the private message commmand
    def privMsgHandler(self, prefix, cmd, args):

        user = prefix[1:].split('!', 1)[0]

        self.privMsg(self.channel.channelName, user +
                     ' ' + random.choice(self.botFacts))

    # handler for the !hello command
    def helloHandler(self):

        messageToSend = 'Hello, my name is ' + self.nickName + \
            '. The current date is ' + str(datetime.now().strftime(
                '%d/%m/%Y')) + ' and the current time is ' + str(datetime.now().strftime('%H:%M'))
        self.privMsg(self.channel.channelName, messageToSend)

    # handler for the !slap command
    def slapHandler(self):

        slapMsg = random.choice([x for x in self.channel.channelClients if x != self.nickName]) + \
            " YOU'VE BEEN SLAPPED BY A TROUT!"

        self.privMsg(self.channel.channelName, slapMsg)

    # handler for NICK command (if user changes nick)
    def nickHandler(self, prefix, newNick):
        oldNick = prefix.split('!')[0][1:]
        self.channel.channelClients.remove(oldNick)
        self.channel.channelClients.append(newNick)

    # entry point for the running sequence of the bot
    def runBot(self):
        # get response as list
        response = (self.getResponse()).split('\r\n')[:-1]

        # checking for blank response
        if response != []:
            self.responseHandler(response)
            return True
        else:
            return False


# IPv6
# bot = BotClient('thisIsARealPerson', 'realHuman',
#                 '#test', 'fc00:1337::17', 6667)

bot = BotClient('thisIsARealPerson', 'realHuman',
                '#test', '::1', 6667)
# running bot sequence
if bot.connectToServer():

    # infinite loop to run the bot functionallity
    while True:

        # running the bot as long as connected to server
        if bot.runBot() == False:
            print('ERROR: CONNECTION TO SERVER LOST\n')

            # 3 attempts to reconnect to the server
            for attempt in range(3):
                print('Attempt (%d), trying to reconnect to the server...\n' %
                      (attempt+1))

                # delay incase required for server to restart
                sleep(2)
                if bot.connectToServer() != False:
                    # connection restablished
                    break
                elif attempt >= 2:
                    print('AFTER 3 ATTEMPTS THE CONNECTION COULD NOT BE ESTABLISHED')
                    exit(1)
                else:
                    continue
        else:
            continue
else:
    print('\nERROR: could not connect to server')
    print('Server IP: ' + bot.server)
    print('Port No: %d\n' % bot.port)
