# coding=utf-8
from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver

class Core(LineReceiver):

    def __init__(self, servers):
        self.servers = servers
        self.id = None

    def connectionMade(self):
        pass
    def connectionLost(self, reason):
        pass
    def lineReceived(self, line):
        pass



class CoreFactory(Factory):

    def __init__(self):
        self.servers = {} # maps server IDs to instances of the protocol

    def buildProtocol(self, addr):
        return Core(self.servers)