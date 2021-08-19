""" Protocol-related exceptions. """

from diffusion.internal.exceptions import DiffusionError


class ProtocolError(ConnectionError, DiffusionError):
    """ General protocol error. """


class ServerConnectionError(ProtocolError):
    """ General error when connecting to server. """


class ServerConnectionResponseError(ServerConnectionError):
    """ Error when the server returns a non-OK code on connection. """

    def __init__(self, response_code):
        super().__init__(f"Failed to connect: {response_code.name}")
        self.response_code = response_code


class ServiceMessageError(ProtocolError):
    """ Error when handling service messages. """


class AbortMessageError(ServiceMessageError):
    """ Abort message received from the server. """


# Conversation errors.


class ConversationError(DiffusionError):
    """ Base conversation error. """


class CIDGeneratorExhaustedError(ConversationError):
    """ Error stating that a CID generator was exhausted. """


class NoSuchConversationError(ConversationError):
    """ The conversation with this CID does not exist in the `ConversationSet`. """

    def __init__(self, cid):
        super().__init__(f"Unknown conversation {cid}")
