import json


class HyperError(Exception):
    def __init__(self, status=None, message=None):
        self.status = status
        self.message = message


class AuthenticationError(HyperError):
    def __str__(self):
        return "No API key provided. (HINT: set your API key using 'hyper.api_key = <API-KEY>'. You can generate API " \
               "keys from the Hyper web interface. See https://hyper.co/developers for details, " \
               "or email support@hyper.co if you have any questions. "


class InvalidRequestError(HyperError):
    def __str__(self):
        try:
            response = json.loads(self.message)
            error = f'Request failed with status code {self.status}: {response["error"]["message"]}'
        except (ValueError, KeyError):
            error = f'Request failed with status code {self.status}: {self.message}'

        return error
