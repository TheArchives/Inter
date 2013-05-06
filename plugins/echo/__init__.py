# coding=utf-8
__author__ = "Gareth Coles"

import json
from system.plugin import Plugin
from system import config as conf
from system.events import manager

class EchoPlugin (Plugin):

    """
    An example plugin.
    Sends received data back down to the client.
    """

    def __init__(self):
        super(EchoPlugin, self).__init__()

    def setup(self):
        self.config = conf.conf()
        if not self.config.get_mapping("echo"):
            self.config.save_mapping("echo", "echo.yml")
            self.config.save_file("echo.yml", {"enabled": True})
            self.config.reload()
        self.events = manager.manager()
        self.events.addCallback("dataReceived", self, self.onDataReceived, 10)

    def onDataReceived(self, event):
        if self.config.get("echo")["enabled"]:
            event.caller.send(json.dumps(event.data))