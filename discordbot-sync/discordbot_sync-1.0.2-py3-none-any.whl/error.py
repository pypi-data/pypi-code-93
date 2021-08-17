class DiscordError(Exception):
    pass

class BotAlreadyRunning(DiscordError):
    pass

class CallbackError(DiscordError):
    pass

'''
    HTTP
'''
class HTTPError(DiscordError):
    pass

class HTTPBadRequest(HTTPError):
    pass

class UnexpectedResponse(HTTPError):
    pass

class RateLimited(HTTPError):
    pass

class MessageSendFailure(HTTPError):
    pass

'''
    Gateway
'''
class GatewayError(DiscordError):
    pass

class ReceivedInvalidPayload(GatewayError):
    pass
    
class InvalidEventPayload(GatewayError):
    pass

class SentInvalidPayload(GatewayError):
    pass

class UnexpectedClose(GatewayError):
    pass

class ReceivedInvalidEvent(ReceivedInvalidPayload):
    pass

class InvalidAPIObject(GatewayError):
    pass