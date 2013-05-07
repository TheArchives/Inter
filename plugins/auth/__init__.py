# coding=utf-8
__author__ = "Gareth Coles"

import json
import logging
from system.plugin import Plugin
from system import config as conf
from system.events import manager


class AuthPlugin (Plugin):

    """
    Authentication plugin.
    This plugin needs to have the highest priority callbacks.

    Checks every incoming JSON message for an API key. If the API key is invalid or missing, it sends an error and
        closes the connection, also cancelling the event.
    """

    def __init__(self):
        super(AuthPlugin, self).__init__()

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

    def onDataReceived(self, event):
        data = event.data
        self.config.reload_mapping("auth")

        if "api_key" in data:
            conf = self.config.get("auth")
            for x, y in conf["keys"].items():
                if data["api_key"] == x:
                    if not event.caller.authenticated:
                        self.logger.info("Client authenticated: %s" % y)
                        event.caller.authenticated = True
                    return
            event.cancel()
            if event.caller.authenticated:
                event.caller.send(json.dumps({"error": "Your API key has been revoked."}))
            else:
                event.caller.send(json.dumps({"error": "Your API key is invalid."}))
            event.caller.transport.loseConnection()

        else:
            event.cancel()
            event.caller.send(json.dumps({"error": "You did not provide an API key."}))
            event.caller.transport.loseConnection()

    def onProtocolBuiltEvent(self, event):
        event.protocol.authenticated = False
        self.logger.debug("Added `authenticated` flag to protocol object.")