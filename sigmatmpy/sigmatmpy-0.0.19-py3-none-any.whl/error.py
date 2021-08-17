name = "sigmatmpy"
import requests
import json
import asyncio
import websocket 

class InputError(Exception):
    """Exception raised for errors in the input.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, message):

        self.message = message
        super().__init__(self.message)

class InvalidAuthorizationError(Exception):
    """Exception raised for errors in the input.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, message):

        self.message = message
        super().__init__(self.message)