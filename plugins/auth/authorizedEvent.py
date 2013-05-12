# coding=utf-8
__author__ = "Gareth Coles"

from system.events.event import Event


class authorizedEvent(Event):
    """
    Event fired when a client is authorized.

    Client available through event.protocol
    """
    def __init__(self, caller, protocol):
        super(authorizedEvent, self).__init__(caller)
        self.protocol = protocol