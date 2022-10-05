# -----------------------------------------------------------
# Creates a bot that acts as a client that can interact with an IRC server
#
# (C) David Topping, Christian Zlatanov, Caleb Harmon, Victor Iyida
# https://github.com/davidtopping02/IRCProj
# -----------------------------------------------------------

# import network socket
import socket
from time import sleep


class BotClient:

    def __init__(self, user, nickName, channel, server, port):

        # init object attributes
        self.userName = user
        self.nickName = nickName
        self.currentChannel = channel
        self.server = server
        self.port = port
        self.channelUsers = None

        # TODO
        # self.hostName = None
        # self.

        # create socket object to gain access to the server
        self.netSocket = socket.socket()

    def connectToServer(self):
        """
        Joins an IRC server from IP address and port, returns false if the connection was unsuccessful
        """
        try:
            # connect to server
            self.netSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.netSocket.connect((self.server, self.port))

            # initial joining server sequence
            self.user(self.userName)
            self.nick(self.nickName)
            self.join(self.currentChannel)
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

    # leave a channel
    def part(self):
        pass

    # leave a server with an optional leaving message
    def quit(self, message=None):
        pass

    # lists all channels on the current network
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
    def names(self, channel):
        pass

    # sends a private message to a user
    def privMsg(self, nickName, message):
        self.sendCMD("PRIVMSG", nickName + " " + message)

    # pong function replies to the ping from server
    def pongReply(self):
        self.sendCMD("PONG", "reply")

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
            pass
        else:
            sleep(2)


# init bot client object
bot = BotClient("thisIsARealPerson", "realHuman",
                "#test", "10.0.42.17", 6667)

# running bot sequence
if bot.connectToServer():

    while True:

        bot.runBot()
else:
    print("could not connect to server")
