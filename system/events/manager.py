# coding=utf-8
import logging
from operator import itemgetter

__author__ = "Gareth Coles"

from system.decorators import Singleton


@Singleton
class EventManager(object):

    """
    The event manager.

    This class is a singleton in charge of managing both events and callbacks. Use EventManager.Instance() or the
        manager() function below to grab an instance.

    You'll probably want to read the Github documentation to learn how, when and why you would use this.

    Remember, priority is handled from highest to lowest, in that order. Try not to pick a priority that's the same
        as another plugin - If you do, order will fall back to alphabetical plugin name ordering.

    Public methods:
        addCallback(callback, plugin, function, priority, cancelled=False):
            Add a callback. Call this from your plugin to handle events.
            Note: A plugin may not have more than one handler for a callback. You should register a function to call
                your handlers in order inside your plugin if you need this. A handler handler. Handlerception!
            - callback:  The name of the callback
            - plugin:    Your plugin object's instance (or self)
            - function:  The callback function
            - priority:  An integer representing where in the order of callbacks the function should be called
            - cancelled: Defaults to False; whether to pass cancelled events in or not
        getCallback(callback, plugin):
            Get a handler dict for a specific callback, in a specific plugin.
            Note: `plugin` is the name of a plugin, not a plugin object.
        getCallbacks(callback):
            Get all handlers (in a list) for a specific callback.
        hasCallback(callback):
            Check if a callback exists.
        hasPluginCallback(callback, plugin):
            Check if a plugin registered a handler for a certain callback.
            Note: `plugin` is the name of a plugin, not a plugin object.
        removeCallback(callback, plugin):
            Remove a callback from a plugin.
            Note: `plugin` is the name of a plugin, not a plugin object.
        removeCallbacks(callback):
            Remove a certain callback.
        removeCallbacksForPlugin(plugin):
            Remove all handlers for a certain plugin.
            Note: `plugin` is the name of a plugin, not a plugin object.
        runCallback(callback, event):
            Run all handlers for a certain callback with an event.
    """

    callbacks = {}
        # {"callbackname": [{"name": name, "priority": prioriy, "function": function, "cancelled": cancelled]}

    def __init__(self):
        self.logger = logging.getLogger("Events")

    def _sort(self, lst):
        return sorted(lst, key=itemgetter("priority", "name"), reverse=True)

    def addCallback(self, callback, plugin, function, priority, cancelled=False):
        if not self.hasCallback(callback):
            self.callbacks[callback] = []
        if self.hasPluginCallback(callback, plugin.info.name):
            raise ValueError("Plugin '%s' has already registered a handler for the '%s' callback" %
                             (plugin.info.name, callback))

        current = self.callbacks[callback]

        data = {"name": plugin.info.name,
                "function": function,
                "priority": priority,
                "cancelled": cancelled}

        self.logger.debug("Adding callback: %s" % data)

        current.append(data)

        self.callbacks[callback] = self._sort(current)

    def getCallback(self, callback, plugin):
        if self.hasCallback(callback):
            callbacks = self.getCallbacks(callback)
            for cb in callbacks:
                if cb["name"] == plugin:
                    return cb
            return None
        return None

    def getCallbacks(self, callback):
        if self.hasCallback(callback):
            return self.callbacks[callback]
        return None

    def hasCallback(self, callback):
        return callback in self.callbacks

    def hasPluginCallback(self, callback, plugin):
        if self.hasCallback(callback):
            callbacks = self.getCallbacks(callback)
            for cb in callbacks:
                if cb["name"] == plugin:
                    return True
            return False
        return False

    def removeCallback(self, callback, plugin):
        if self.hasPluginCallback(callback, plugin):
            callbacks = self.getCallbacks(callback)
            done = []
            for cb in callbacks:
                if not cb["name"] == plugin:
                    done.append(cb)
            if len(done) > 0:
                self.callbacks[callback] = self._sort(done)
            else:
                del self.callbacks[callback]

    def removeCallbacks(self, callback):
        if self.hasCallback(callback):
            del self.callbacks[callback]

    def removeCallbacksForPlugin(self, plugin):
        current = self.callbacks.items()
        for key, value in current:
            done = []
            for cb in value:
                if not cb["name"] == plugin:
                    done.append(cb)
            if len(done) > 0:
                self.callbacks[key] = self._sort(done)
            else:
                del self.callbacks[key]

    def runCallback(self, callback, event):
        if self.hasCallback(callback):
            for cb in self.getCallbacks(callback):
                self.logger.debug("Running callback: %s" % cb)
                if event.cancelled:
                    if cb["cancelled"]:
                        cb["function"](event)
                    else:
                        self.logger.debug("Not running, event is cancelled and handler doesn't accept cancelled events")
                else:
                    cb["function"](event)

def manager():
    """
    Get yourself an instance of the event manager.
    """
    return EventManager.Instance()