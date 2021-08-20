import aiohttp


class OkexAPIException(Exception):
    def __init__(self, response: aiohttp.ClientResponse, error_msg: str, error_code: str = None, extra=None):
        self.message = error_msg
        self.error_code = int(error_code)
        self.status_code = response.status
        self.response = response
        self.request = getattr(response, 'request', None)
        self.extra = extra

    def __str__(self):  # pragma: no cover
        info = f'Okex APIError({self.error_code}): {self.message}'
        if self.extra:
            info += f", extra:{self.extra}"
        return info
