# -----------------------------------------------------------
# Creates a bot that acts as a client that can interact with an IRC server
#
# (C) David Topping, Christian Zlatanov, Caleb Harmon, Victor Iyida
# https://github.com/davidtopping02/IRCProj
# -----------------------------------------------------------

# import network socket
import socket


class BotClient:

    def __init__(self, nickName, password):

        # self.server =  #valid server
        self.port = 6667
        self.channel = "#test"
        self.nickName = nickName
        self.password = password
        self.IRCSocket = None

        # this creates an IRC server object: other part of the project
        # ircServer = IRCServer()

    def joinServer(self):
        # ircServer.connect(self.server, self.port, slef.channel, self.nickName, self.password)
        pass

    def joinMiniircdTESTING(self):
        """
        Joins to a miniircd server, used for testing the bot functionallity but does it will connect to our own IRC server for submission
        """

        # creates socket object
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.IRCSocket:

            # encode data for tramsmission
            delimeter = " : ".encode()
            user = self.nickName.encode()
            message = "test123".encode()

            # connect to IRC server
            self.IRCSocket.connect(("10.0.24.4", self.port))

            # send message
            self.IRCSocket.sendall(user + delimeter + message)

            while (True):
                message = input().encode()
                self.IRCSocket.sendall(user + delimeter + message)
                data = self.IRCSocket.recv(1024)
                print(f"Received {data!r}")

    def joinchannel():
        pass

    def respondPrivMsg():
        pass

    def respondChannelCMD():
        pass


bot = BotClient("david", "test")
bot.joinMiniircdTESTING()

# conncet to server

# get response from server

# so on...
