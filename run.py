# coding=utf-8

from twisted.internet import reactor
from system.core import CoreFactory

reactor.listenTCP(8123, CoreFactory())
reactor.run()