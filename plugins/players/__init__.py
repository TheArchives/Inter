# coding=utf-8
__author__ = "Gareth Coles"

import json
import logging
from system.plugin import Plugin
from system import config as conf
from system.events import manager

class PlayersPlugin (Plugin):

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
        super(PlayersPlugin, self).__init__()

    def setup(self):
        self.config = conf.conf()
        self.logger = logging.getLogger("Players")
        self.events = manager.manager()
        self.events.addCallback("dataReceived", self, self.onDataReceived, 0)
        self.events.addCallback("protocolBuilt", self, self.onProtocolBuiltEvent, 99999)

    def sendToOthers(self, current, message):
        cur = current.name
        all_servers = {}

        for x, y in current.factory.servers.items():
            all_servers[x] = y

        names = []
        for x, y in all_servers.items():
            names.append(x)

        self.logger.debug("Servers: %s" % names)

        if cur in all_servers:
            del all_servers[cur]

        for name, server in all_servers.items():
            self.logger.debug("Sending message to server %s: %s" % (name, message))
            server.send(message)

    def onDataReceived(self, event):
        if event.caller.authenticated:
            data = event.data
            if not "action" in data:
                return
            if data["action"] == "players":
                if data["type"] == "online":
                    self.logger.debug("Player connected to %s: %s." % (event.caller.name, data["player"]))
                    event.caller.players.append(data["player"])
                    self.sendToOthers(event.caller,
                                      json.dumps({"from": "players", "type": "online", "player": data["player"],
                                                  "target": event.caller.name})
                                      )
                elif data["type"] == "offline":
                    if data["player"] in event.caller.players:
                        self.logger.debug("Player disconnected from %s: %s." % (event.caller.name, data["player"]))
                        event.caller.players.remove(data["player"])
                        self.sendToOthers(event.caller,
                                          json.dumps({"from": "players", "type": "offline", "player": data["player"],
                                                      "target": event.caller.name})
                                          )
                elif data["type"] == "list":
                    if "target" in data:
                        if data["target"] in event.caller.factory.servers:
                            self.logger.debug("Server %s requested players from server %s." % (event.caller.name,
                                                                                              data["target"]))
                            json_data = json.dumps({"from": "players",
                                                    "players": event.caller.factory.servers[data["target"]].players,
                                                    "type": "list",
                                                    "target": data["target"]})
                        else:
                            json_data = json.dumps({"from": "players", "error": "Unknown server: %s" % data["target"]})
                    else:
                        self.logger.debug("Server %s requested players from all servers." % event.caller.name)
                        all_players = {}

                        for name, obj in event.caller.factory.servers.items():
                            if not name == event.caller.name:
                                all_players[name] = obj.players
                        json_data = json.dumps({"from": "players", "players": all_players, "target": "all",
                                                "type": "list"})

                    event.caller.send(json_data)
                else:
                    json_data = json.dumps({"from": "players", "error": "Unknown action type: %s" % data["type"]})
                    event.caller.send(json_data)

    def onProtocolBuiltEvent(self, event):
        event.protocol.players = []
        self.logger.debug("Added `players` variable to protocol object.")

        pass