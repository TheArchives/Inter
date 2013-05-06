# coding=utf-8
__author__ = "Gareth Coles"

import logging
from system.plugin import Plugin
from system import config as conf
from system.events import manager


class HelloPlugin (Plugin):

    """
    An example plugin.
    Some guidelines for plugin class writing..

    All plugins must inherit from system.plugin.Plugin

    In line with Python class inheritence, calling the super class' __init__ function is recommended.
    See system/plugin.py for more details on how writing plugins works.
    """

    def __init__(self):
        super(HelloPlugin, self).__init__()

    def setup(self):
        self.config = conf.conf()
        if not self.config.get_mapping("hello"):
            self.config.save_mapping("hello", "hello.yml")
            self.config.save_file("hello.yml", {"message": "Hello, world!"})
            self.config.reload()
        self.events = manager.manager()
        self.events.addCallback("dataReceived", self, self.onDataReceived, 1)
        self.logger.info(self.config.get("hello")["message"])

    def onDataReceived(self, event):
        self.logger.info(self.config.get("hello")["message"])