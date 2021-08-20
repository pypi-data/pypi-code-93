# coding: utf-8

###############################################################
#
#   STANDARD IMPORTS
#


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
#   CLASSE DEFINITIONS
#


class RDPItemStreamCallback(object):
    """
    an RDP item stream callback functions
    """

    def __init__(
        self, on_ack_cb=None, on_response_cb=None, on_update_cb=None, on_alarm_cb=None
    ):
        #   callback functions
        self._on_ack_cb = on_ack_cb
        self._on_response_cb = on_response_cb
        self._on_update_cb = on_update_cb
        self._on_alarm_cb = on_alarm_cb

    @property
    def on_ack(self):
        """Called when an ack is received.
        This callback receives an utf-8 string as argument.

        Default: None

        Returns
        -------
        callable object
        """
        return self._on_ack_cb

    @on_ack.setter
    def on_ack(self, on_ack_cb):
        self._on_ack_cb = on_ack_cb

    @property
    def on_response(self):
        """Called when a reponse is received.
        This callback receives an utf-8 string as argument.

        Default: None

        Returns
        -------
        callable object
        """
        return self._on_response_cb

    @on_response.setter
    def on_response(self, on_response_cb):
        self._on_response_cb = on_response_cb

    @property
    def on_update(self):
        """Called when a update is received.
        This callback receives an utf-8 string as argument.

        Default: None

        Returns
        -------
        callable object
        """
        return self._on_update_cb

    @on_update.setter
    def on_update(self, on_update_cb):
        self._on_update_cb = on_update_cb

    @property
    def on_alarm(self):
        """Called when a alarm is received.
        This callback receives an utf-8 string as argument.

        Default: None

        Returns
        -------
        callable object
        """
        return self._on_alarm_cb

    @on_alarm.setter
    def on_alarm(self, on_alarm_cb):
        self._on_alarm_cb = on_alarm_cb
