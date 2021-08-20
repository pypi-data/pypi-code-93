import aiohttp


class HuobiAPIException(Exception):
    def __init__(self, response: aiohttp.ClientResponse, error_msg: str, error_code=None):
        self.message = error_msg
        self.status_code = response.status
        self.response = response
        self.request = getattr(response, 'request', None)
        self.error_code = error_code

    def __str__(self):  # pragma: no cover
        return f'HuobiAPIError({self.error_code}): {self.message}'
