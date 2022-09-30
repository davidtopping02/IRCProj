class Server:
    def __init__(self, hostPort, hostIP, connectedClients, rawLog):
        self.hostPort = hostPort
        self.hostIp = hostIP
        self.connectedClients = connectedClients
        self.rawLog = rawLog


class Client:
    def __init__(self, nickName, realName, user, port, clientIP,):
        self.nickName = nickName
        self, realName = realName
        self.user = user
        self.port = port
        self.clientIP = clientIP


class Chamnel:
    def __init__(self, serverConnection, channelName, channelClients, channelTopic):
        self.serverConnection = serverConnection
        self.channelName = channelName
        self.channelClients = channelClients
        self.channelTopic = channelTopic
