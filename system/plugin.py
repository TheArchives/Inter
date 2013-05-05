# coding=utf-8
__author__ = "Gareth Coles"

import logging
from yapsy.IPlugin import IPlugin


class Plugin(IPlugin):
    """
    Super class for creating plugins.

    Inherit this class when you create your plugin's core class. You may override the following methods. Be sure to
        call the super class' version of these functions!
    - activate(self): Called when the plugin is loaded.
      - Don't use this for setup, needed variables will be missing!
    - deactivate(self): Called when the plugin is unloaded.
      - Use this to clean up. May be useful for saving data and the like.
    - setup(self, info, factory): Called when the plugin is loaded. Be sure to store the info and factory args!
      - Do any required setup of your plugin here.

    Optionally, you can override the `activate` method, but this is not required and should not be used for setup.
    """

    def __init__(self):
        super(Plugin, self).__init__()

    def _add_variables(self, info, factory):
        """
        Do not override this unless absolutely necessary!
        This function is used to store essential data required for a plugin to function properly.
        It also sets up logging.

        ..no really, don't overload this. Yeah, I'm talking to you. This method is not your type(). Find somefunc else.
            I understand that we're all consenting adults here, but sometimes.. It's best not to go there.

        :param info:    PluginInfo  - Information related to this plugin.
        :param factory: CoreFactory - Use this to interact directly with connected clients.
        """
        self.info = info
        self.module = self.info.path.replace("\\", "/").split("/")[-1]
        self.logger = logging.getLogger(self.module.title())
        self.factory = factory

    def activate(self):
        """
        Called when the plugin is loaded. Not to be used for setup!
        """
        super(Plugin, self).activate()

    def deactivate(self):
        """
        Called when the plugin is unloaded. Use this for saving data or cleaning up.
        """
        super(Plugin, self).deactivate()

    def setup(self):
        """
        Called when the plugin is loaded. This is used for setting up the plugin.
        Don't use activate for this. self.info and self.factory are only available once this method is called.
        """
        pass