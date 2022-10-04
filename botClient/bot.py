# -----------------------------------------------------------
# Creates a bot that acts as a client that can interact with an IRC server
#
# (C) David Topping, Christian Zlatanov, Caleb Harmon, Victor Iyida
# https://github.com/davidtopping02/IRCProj
# -----------------------------------------------------------

# import network socket
import socket


class BotClient:

    def __init__(self, user, nickName, channel, server, port):

        # init object attributes
        self.userName = user
        self.nickName = nickName
        self.currentChannel = channel
        self.server = server
        self.port = port

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
            print(cmd + " " + args + "\n")
        except:
            print("Message could not be sent, please try again")

    # revieves any messages from the server
    def getResponse(self):
        try:
            return self.netSocket.recv(2000).decode("ascii")
        except:
            return "Error recieving data from the server"

    def join(self, newChan=None):
        self.currentChannel = newChan
        self.sendCMD("JOIN", newChan)

    def part(self):
        # used to leave a channel
        pass

    def quit(self, message=None):
        # used to leave a server with an optional leaving message
        pass

    def list(self):
        # lists all channels on the current network
        pass

    # changes/sends bots nickname
    def nick(self, newNick=None):
        self.nickName = newNick
        self.sendCMD("NICK", self.nickName)

    # sets the user name of the bot
    def user(self, user=None):
        self.userName = user
        self.sendCMD("USER", self.nickName + " " + self.nickName +
                     " " + self.nickName + " " + self.userName)

    def names(self, channel):
        # shows the nicks of all users on channel parameter
        pass

    def msg(self, nickName, message):
        # sends a private message to a user
        pass

    def respondPrivMsg():
        pass

    def respondChannelCMD():
        pass


# init bot client and connect to server
bot = BotClient("thisIsARealPerson", "bottyBot123",
                "#mainChan", "10.0.42.17", 6667)

# running bot sequence
if bot.connectToServer():

    while True:
        recievedText = bot.getResponse()
        print(recievedText)
else:
    print("could not connect to server")
