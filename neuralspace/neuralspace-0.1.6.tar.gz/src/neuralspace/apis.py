import aiohttp

__ASYNC_HTTP_SESSION = None


def get_async_http_session() -> aiohttp.ClientSession:
    global __ASYNC_HTTP_SESSION
    if __ASYNC_HTTP_SESSION is None:
        __ASYNC_HTTP_SESSION = aiohttp.ClientSession()
    return __ASYNC_HTTP_SESSION
