# coding=utf-8
import logging

__author__ = "Gareth Coles"


class Event(object):
    """
    Event is.. well, an event. Events represent things that happened; they get passed to callback handlers.
    the Event class itself should not be used directly. Instead, you should inherit it and create your own event.
    """

    cancelled = False  # Don't override this.
    caller = None  # Don't override this either.

    def __init__(self, caller):  # Don't forget to make a call to the super class!
        self.logger = logging.getLogger("Event")
        self.caller = caller

    def cancel(self):  # It's okay to not override this too. You probably won't need to, either.
        """
        Cancel the event.
        Once an event has been cancelled, only other plugins that specifically handle cancelled events will see it.

        There's no method for uncancelling events. Please don't make one either.
        """
        self.cancelled = True


class clientConnectedEvent(Event):
    """
    Event fired when a client connects.

    Client available through event.caller
    """

    def __init__(self, caller):
        super(clientConnectedEvent, self).__init__(caller)


class clientDisconnectedEvent(Event):
    """
    Event fired when a client disconnects.

    Client available through event.caller
    """

    def __init__(self, caller):
        super(clientDisconnectedEvent, self).__init__(caller)


class dataReceivedEvent(Event):
    """
    Event fired when a client recieves some data.

    Client available through event.caller
    Data available through event.data
    """

    def __init__(self, caller, data):
        super(dataReceivedEvent, self).__init__(caller)
        self.data = data

class pingSentEvent(Event):
    """
    Event fired when a ping is sent to a client.
    """

    def __init__(self, caller, timestamp):
        super(pingSentEvent, self).__init__(caller)
        self.timestamp = timestamp

class pongReceivedEvent(Event):
    """
    Event fired when a client recieves a pong.
    """

    def __init__(self, caller, timestamp):
        super(pongReceivedEvent, self).__init__(caller)
        self.timestamp = timestamp

class pluginLoadedEvent(Event):
    """
    Event fired when a plugin is loaded (Not necessarily your one, make sure you do the necessary checking!)

    PluginInfo object available through event.plugin
    """

    def __init__(self, caller, plugin):
        super(pluginLoadedEvent, self).__init__(caller)
        self.plugin = plugin


class pluginsLoadedEvent(Event):
    """
    Event fired when all the plugins have finished loading.
    """

    def __init__(self, caller):
        super(pluginsLoadedEvent, self).__init__(caller)


class protocolBuiltEvent(Event):
    """
    Event fired when a client's protocol object has been built.

    This is only provided in case you need to modify the protocol object before it is used.
    More than likely, you won't need this event at all.

    Protocol object is available through event.protocol
    """

    def __init__(self, caller, protocol):
        super(protocolBuiltEvent, self).__init__(caller)
        self.protocol = protocol