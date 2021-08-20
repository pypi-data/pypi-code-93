# coding: utf-8

###############################################################
#
#   STANDARD IMPORTS
#

from enum import Enum, unique

from threading import Lock

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


@unique
class StreamState(Enum):
    """Define the state of the Stream.

    Closed  :    The Stream is closed and ready to be opened.
    Pending :    The Stream is in a pending state. Upon success, the Stream will move into an open state,
                    otherwise will be closed.
    Open    :    The Stream is opened.
    Pause   :    The Stream is paused.
    """

    Closed = 1
    Pending = 2
    Open = 3
    Pause = 4


class State(object):
    """ this class is designed for store the state of stream """

    def __init__(self, *args, **kwargs):
        #   state of stream
        self._state = StreamState.Closed
        self._state_lock = Lock()

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, val):
        with self._state_lock:
            self._state = val
