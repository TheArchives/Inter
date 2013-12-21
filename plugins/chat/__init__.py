# coding=utf-8
from operator import itemgetter

__author__ = "Gareth Coles"

import time
import json
import logging

from system.plugin import Plugin
from system import config as conf
from system.events import manager


class ChatPlugin (Plugin):

    """
    Chat plugin.
        This plugin will log and relay chat messages between server.
        It will also keep a chat buffer for web clients to pull down periodically.

    Error codes:
        1 | The target specified was not found. | Alert the user and continue. | WARN
    """

    history = []

    def __init__(self):
        super(ChatPlugin, self).__init__()

    def setup(self):
        self.config = conf.conf()
        self.logger = logging.getLogger("Chat")
        self.events = manager.manager()
        self.events.addCallback("dataReceived", self, self.onDataReceived, 100)

    def saveMessage(self, message):
        """
        Saves a message to the buffer, dropping messages if we have over 100 saved.
        :param message:
        """
        self.history.append(message)
        self.history = sorted(self.history, key=itemgetter("time"))
        while len(self.history) > 100:
            self.history.pop(0)

    def onDataReceived(self, event):
        data = event.data
        curtime = time.time()

        if "action" in data:
            if data["action"] == "chat":
                message = data["message"]
                user = data["user"]
                target = None
                smessage = {"message": data["message"], "time": curtime, "user": data["user"],
                            "source": event.caller.name}
                if "target" in data:
                    target = data["target"]
                    smessage["target"] = data["target"]

                self.saveMessage(smessage)

                self.logger.info("<%s@%s> %s" % (data["user"], event.caller.name, data["message"]))

                if target:
                    if target in self.factory.servers:
                        self.factory.servers[target].send(json.dumps({"from": "chat", "source": event.caller.name,
                                                                      "time": curtime, "message": message, "user": user}))
                    else:
                        event.caller.send(json.dumps({"from": "chat", "error": "Unable to locate server: " + target,
                                                      "code": 1}))
                else:
                    event.caller.sendToOthers(json.dumps({"from": "chat", "source": event.caller.name,
                                                          "time": curtime, "message": message, "user": user}))

            elif data["action"] == "chat-history":
                pass
