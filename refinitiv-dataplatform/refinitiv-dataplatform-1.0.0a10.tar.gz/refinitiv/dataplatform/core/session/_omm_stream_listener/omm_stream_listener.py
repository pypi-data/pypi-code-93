# coding: utf-8

###############################################################
#
#   STANDARD IMPORTS
#

__all__ = ["OMMStreamListener"]


import abc

###############################################################
#
#   REFINITIV IMPORTS
#

###############################################################
#
#   LOCAL IMPORTS
#

###############################################################
#
#   CLASS DEFINITIONS
#


class OMMStreamListener(abc.ABC):
    """ " This abstract class is designed to let the user to implement open message model (OMM) stream.

    Available notifications from the stream are (only the asterisk are now supported):
    - ack message
    - error message*
    - generic message
    - post message
    - refresh message*
    - status message*
    - update message*
    - complete message* (this is a special when the update message has a complete flag)
    """

    def __init__(self, name, service=None, fields=None, domain="MarketPrice"):
        self._service = service
        self._name = name
        self._fields = fields
        self._domain = domain
        self._id = None

    @property
    def service(self):
        return self._service

    @property
    def name(self):
        return self._name

    @property
    def fields(self):
        return self._fields

    @property
    def domain(self):
        return self._domain

    @property
    def id(self):
        return self._id

    ###############################################################
    #   callback functions when received messages
    @abc.abstractmethod
    def on_refresh(self, stream, message):
        pass

    @abc.abstractmethod
    def on_update(self, stream, update):
        pass

    @abc.abstractmethod
    def on_status(self, stream, status):
        pass

    @abc.abstractmethod
    def on_complete(self, stream):
        pass

    @abc.abstractmethod
    def on_error(self, stream, error):
        pass
