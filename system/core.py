# coding=utf-8

import json
import logging
import time

from twisted.internet.protocol import Factory, connectionDone
from twisted.internet import reactor
from twisted.protocols.basic import LineReceiver
from yapsy.PluginManager import PluginManagerSingleton
from system import util
from system.events import manager
from system.events.event import clientConnectedEvent, clientDisconnectedEvent, dataReceivedEvent, pluginLoadedEvent, \
    pluginsLoadedEvent, protocolBuiltEvent, pingSentEvent, pongReceivedEvent

import system.globals as g


class Core(LineReceiver):
    """
    Core networking and parsing.
    This class is the `core` of the application and is responsible for individual connections.
    """

    host = ""
    pings = []

    def __init__(self, factory, addr):
        self.factory = factory
        self.host = addr.host
        self.logger = logging.getLogger("Protocol")
        self.events = manager.manager()
        self.id = None

    def ping(self):
        if not self.connected:
            return
        if len(self.pings) > 2:
            self.send(json.dumps({"error": "Ping timeout", "from": "core"}))
            self.transport.loseConnection()
            return
        now = str(time.time())

        self.debug("Sending ping: %s" % now)

        self.send(json.dumps({"from": "ping", "timestamp": now}))
        self.pings.append(now)

        event = pingSentEvent(self, now)
        self.events.runCallback("pingSent", event)
        reactor.callLater(30, self.ping)

    def connectionMade(self):
        """
        Called when a client connection is made.
        """
        # host = self.transport.getPeer().host
        # port = self.transport.getPeer().port
        data = json.dumps({"version": g.__version__})
        self.send(data)
        self.ping()
        event = clientConnectedEvent(self)
        self.events.runCallback("clientConnected", event)

    def connectionLost(self, reason=connectionDone):
        """
        Called when the client loses connection.
        :param reason: Why the client lost connection.
        """

        self.connected = 0

        event = clientDisconnectedEvent(self)
        self.events.runCallback("clientDisconnected", event)
        self.info("Disconnected: %s" % reason.getErrorMessage())
        self.factory.clients.remove(self)

    def lineReceived(self, line):
        """
        Called when a line is recieved from the client. Must end with '\n'.
        :param line: The data recieved.
        """
        self.debug("Data: %s" % line.rstrip("\n"))
        try:
            data = json.loads(line)
        except ValueError:
            self.warn("Unable to parse JSON: %s" % line.rstrip("\n"))
            data = json.dumps({"error": "No JSON object could be decoded", "from": "core"})
            self.send(data)
        except Exception as e:
            util.output_exception(self)  # Never do this, by the way. Hackish formatting = baaaaaaaad.
            data = json.dumps({"error": str(e), "from": "core"})
            self.sendLine(data)
        else:
            self.debug("Parsed data: %s" % data)

            if "pong" in data:
                pong = data["pong"]

                self.debug("Received pong: %s" % pong)

                self.pings.remove(pong)
                event = pongReceivedEvent(self, pong)
                self.events.runCallback("pingSent", event)
                return

            event = dataReceivedEvent(self, data)
            self.events.runCallback("dataReceived", event)

    def log(self, level, message):
        self.logger.log(level, "%s | %s" % (self.host.rjust(15), message))

    def debug(self, message):
        self.log(logging.DEBUG, message)

    def info(self, message):
        self.log(logging.INFO, message)

    def warn(self, message):
        self.log(logging.WARN, message)

    def error(self, message):
        self.log(logging.ERROR, message)

    def critical(self, message):
        self.log(logging.CRITICAL, message)

    def send(self, data):
        if self.connected:
            self.debug("Sending data: %s" % data)
            self.sendLine(data)

    def sendToOthers(self, data):
        clients = self.factory.clients
        for client in clients:
            if not client == self:
                client.send(data)


class CoreFactory(Factory):
    """
    Protocol facotry
    This class handles creation of Protocol objects (one per connection) and communication between them.
    It also handles plugin loading and execution.
    """

    def __init__(self):
        self.servers = {}
        self.clients = []
        self.logger = logging.getLogger("Factory")
        self.plugman = PluginManagerSingleton.get()
        self.events = manager.manager()
        self.plugman.setPluginPlaces(["plugins"])
        self.plugman.setPluginInfoExtension("plug")
        self.plugman.collectPlugins()

        self.logger.info("Loading plugins..")
        for pluginInfo in self.plugman.getAllPlugins():
            try:
                self.plugman.activatePluginByName(pluginInfo.name)
                pluginInfo.plugin_object._add_variables(pluginInfo, self)
                pluginInfo.plugin_object.setup()
            except Exception:
                self.logger.warn("Unable to load plugin: %s v%s" % (pluginInfo.name, pluginInfo.version))
                util.output_exception(self.logger, logging.WARN)
                self.plugman.deactivatePluginByName(pluginInfo.name)
            else:
                self.logger.info("Loaded plugin: %s v%s" % (pluginInfo.name, pluginInfo.version))
                event = pluginLoadedEvent(self, pluginInfo)
                self.events.runCallback("pluginLoaded", event)
        self.logger.info("Finished loading plugins.")

        event = pluginsLoadedEvent(self)
        self.events.runCallback("pluginsLoaded", event)

    def buildProtocol(self, addr):
        """
        Builds an instance of the protocol for a client.
        :param addr: IAddress of the client.
        """
        protocol = Core(self, addr)
        event = protocolBuiltEvent(self, protocol)
        self.events.runCallback("protocolBuilt", event)
        protocol.info("Client connecting on port %s" % addr.port)
        self.clients.append(protocol)
        return protocol

    def sendToAll(self, data):
        """
        Send a message to all clients.
        :param data: JSON to send to all connected clients.
        """
        for client in self.clients:
            client.send(data)

    def cleanup(self):
        """
        Cleans up plugins and the like after the program has been asked to terminate.
        """
        self.logger.info("Shutting down..")
        self.logger.info("Dropping clients..")

        for client in self.clients:
            client.send(json.dumps({"error": "Server is shutting down", "from": "core"}))
            client.transport.loseConnection()
            del client

        self.logger.info("Disabling plugins..")
        for pluginInfo in self.plugman.getAllPlugins():
            try:
                self.plugman.deactivatePluginByName(pluginInfo.name)
            except Exception:
                self.logger.warn("Error disabling plugin: %s v%s" % (pluginInfo.name, pluginInfo.version))
                util.output_exception(self.logger, logging.WARN)
            else:
                self.logger.info("Disabled plugin: %s v%s" % (pluginInfo.name, pluginInfo.version))
        self.logger.info("Finished shutting down.")