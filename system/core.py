# coding=utf-8

import json
import logging

from twisted.internet.protocol import Factory, connectionDone
from twisted.internet.error import ConnectionDone
from twisted.protocols.basic import LineReceiver
from yapsy.PluginFileLocator import PluginFileLocator
from yapsy.PluginManager import PluginManager
from system import util

import system.globals as g


class Core(LineReceiver):

    """
    Core networking and parsing.
    This class is the `core` of the application and is responsible for individual connections.
    """

    def __init__(self, factory):
        self.factory = factory
        self.logger = logging.getLogger("Protocol")
        self.id = None

    def connectionMade(self):
        """
        Called when a client connection is made.
        """
        # host = self.transport.getPeer().host
        # port = self.transport.getPeer().port
        data = json.dumps({"version": g.__version__})
        self.sendLine(data)

    def connectionLost(self, reason=connectionDone):
        """
        Called when the client loses connection.
        :param reason: Why the client lost connection.
        """
        self.logger.info("Client %s disconnected: %s" % (self.transport.getPeer().host, reason.getErrorMessage()))

    def lineReceived(self, line):
        """
        Called when a line is recieved from the client. Must end with '\n'.
        :param line: The data recieved.
        """
        self.logger.debug("Data: %s" % line.rstrip("\n"))
        try:
            data = json.loads(line)
        except ValueError:
            data = json.dumps({"error": "No JSON object could be decoded"})
            self.sendLine(data)
        except Exception as e:
            util.output_exception(self.logger)
            data = json.dumps({"error": str(e)})
            self.sendLine(data)
        else:
            self.logger.debug("Parsed data: %s" % data)


class CoreFactory(Factory):
    """
    Protocol facotry
    This class handles creation of Protocol objects (one per connection) and communication between them.
    It also handles plugin loading and execution.
    """

    def __init__(self):
        self.logger = logging.getLogger("Factory")
        self.plugman = PluginManager()
        self.plugman.setPluginPlaces(["plugins"])
        self.plugman.setPluginInfoExtension("plug")
        self.plugman.collectPlugins()
        self.servers = {}
        self.callbacks = {}

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
        self.logger.info("Finished loading plugins.")

    def buildProtocol(self, addr):
        """
        Builds an instance of the protocol for a client.
        :param addr: IAddress of the client.
        """
        self.logger.info("Client connecting - %s:%s" % (addr.host, addr.port))
        return Core(self)

    def addCallback(self, key, func):
        if not key in self.callbacks:
            self.callbacks[key] = [func]
        else:
            callbacks = self.callbacks[key]
            callbacks.append(func)
            self.callbacks[key] = callbacks

    def cleanup(self):
        """
        Cleans up plugins and the like after the program has been asked to terminate.
        """
        self.logger.info("Shutting down..")
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