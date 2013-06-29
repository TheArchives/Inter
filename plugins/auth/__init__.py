# coding=utf-8
__author__ = "Gareth Coles"

import json
import logging
from system.plugin import Plugin
from system import config as conf
from system.events import manager
from authorizedEvent import authorizedEvent


class AuthPlugin (Plugin):

    """
    Authentication plugin.
    This plugin needs to have the highest priority callbacks.

    Checks an incoming JSON message for an API key. If the API key is invalid or missing, it sends an error and
        closes the connection, also cancelling the event. This is only done on the first message.

    Remember, whatever your first message is, it must contain the API key. It can contain other data for the other
        plugins as well, but the API key is required for authentication.

    Error codes:
        1 | You've already authenticated.              | Alert the user and continue. Fix your bug. | WARN
        2 | Another server is using your API key.      | Alert the user and stop.                   | CRITICAL
        3 | Your API key is invalid or not recognized. | Alert the user and stop.                   | CRITICAL
        4 | You didn't provide an API key.             | Alert the user and stop. Fix your bug.     | CRITICAL

    When adding support for error codes to your application, remember that they're plugin-specific. Use the
        `from` key to determine where they're coming from and handle them accordingly.
    """

    def __init__(self):
        super(AuthPlugin, self).__init__()

    def sendToOthers(self, data):
        clients = self.factory.clients
        for client in clients:
            if not client == self:
                if hasattr(client, "authenticated"):
                    if client.authenticated:
                        client.send(data)

    def setup(self):
        self.config = conf.conf()
        self.logger = logging.getLogger("Auth")
        if not self.config.get_mapping("auth"):
            self.config.save_mapping("auth", "auth.yml")
            self.config.save_file("auth.yml", {"keys": {}})
            self.config.reload()
        self.events = manager.manager()
        self.events.addCallback("dataReceived", self, self.onDataReceived, 99999)
        self.events.addCallback("protocolBuilt", self, self.onProtocolBuiltEvent, 99999)
        self.events.addCallback("clientDisconnected", self, self.onClientDisconnected, 0)

    def onDataReceived(self, event):
        if not event.caller.authenticated:
            data = event.data
            self.config.reload_mapping("auth")

            if event.caller.authenticated:
                event.caller.send(json.dumps({"error": "You have already authenticated.",
                                              "from": "auth", "status": "error", "code": 1}))
                return

            if "api_key" in data:
                for x, y in event.caller.factory.servers.items():
                    if data["api_key"] == y.api_key:
                        event.cancel()
                        event.caller.send(json.dumps({"error": "There is already a server with this API key connected",
                                                      "from": "auth", "status": "error", "code": 2}))
                        event.caller.transport.loseConnection()
                        return
                conf = self.config.get("auth")
                for x, y in conf["keys"].items():
                    if data["api_key"] == x:
                        self.logger.info("Client authenticated: %s" % y)
                        event.caller.authenticated = True
                        event.caller.api_key = x
                        event.caller.name = y
                        # event.caller.send(json.dumps({"name": y, "from": "auth",
                        #                               "status": "success"}))
                        if "not_server" in data:
                            if data["not_server"]:
                                event.caller.not_server = True
                                return
                        event.caller.sendToOthers(json.dumps({"from": "auth", "action": "authenticated",
                                                              "name": y, "status": "success"}))
                        event.caller.factory.servers[y] = event.caller
                        authevent = authorizedEvent(self, event.caller)
                        self.events.runCallback("onAuthorized", authevent)
                        return
                event.cancel()
                event.caller.send(json.dumps({"error": "Your API key is invalid.", "from": "auth",
                                              "status": "error", "code": 3}))
                event.caller.transport.loseConnection()
            else:
                event.cancel()
                event.caller.send(json.dumps({"error": "You did not provide an API key.", "from": "auth",
                                              "status": "error", "code": 4}))
                event.caller.transport.loseConnection()

    def onProtocolBuiltEvent(self, event):
        event.protocol.authenticated = False
        event.protocol.not_server = False
        self.logger.debug("Added `authenticated` and `not_server` flags to protocol object.")
        event.protocol.api_key = None
        event.protocol.name = None
        self.logger.debug("Added `name` and `api_key` variables to protocol object.")

        event.protocol._sendToOthers = event.protocol.sendToOthers
        event.protocol.sendToOthers = self.sendToOthers
        self.logger.debug("Overridden sendToOthers function in protocol object.")

    def onClientDisconnected(self, event):
        if event.caller.name:
            del event.caller.factory.servers[event.caller.name]
            self.logger.debug("Removed server '%s' from factory servers dict." % event.caller.name)
        if event.caller.authenticated and not event.caller.not_server:
            event.caller.sendToOthers(json.dumps({"from": "auth", "action": "disconnected", "name": event.caller.name}))