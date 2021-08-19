import aiohttp

_client_session = None


class CommError(Exception):

    def __init__(self, msg, payload=None):
        super().__init__(msg)
        self.payload = payload

    pass


async def http_get_json(url, headers={}):
    return await _http_request_json(url, 'GET', None, headers)


async def http_post_json(url, payload={}, headers={}):
    return await _http_request_json(url, 'POST', payload, headers)


async def http_get(url, headers={}):
    global _client_session
    if _client_session is None:
        _client_session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=600))
    session = _client_session
    async with session.get(url, ssl=False, headers=headers) as r:
        return r, await r.read()


async def http_get_raw(url, headers={}):
    r = http_get(url, headers)
    if not (r.status >= 200 and r.status < 300):
        raise CommError(f'{url} raw get request returns {r.status}', await r.read())
    return await r.read()


async def _http_request_json(url, method, payload, headers={}):
    global _client_session
    if _client_session is None:
        _client_session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=600))
    session = _client_session
    if method == 'GET':
        async with session.get(url, ssl=False, headers=headers) as r:
            # print(r.status,r.json())
            if not (r.status >= 200 and r.status < 300):
                raise CommError(f'{url} {method} returns {r.status}', await r.json())
            return await r.json()
    elif method == 'POST':
        async with session.post(url, ssl=False, json=payload, headers=headers) as r:
            # print(r.status,r.json())
            if not (r.status >= 200 and r.status < 300):
                raise CommError(f'{url} {method} returns {r.status}', await r.json())
            return await r.json()
    elif method == 'PATCH':
        async with session.patch(url, ssl=False, json=payload, headers=headers) as r:
            # print(r.status,r.json())
            if not (r.status >= 200 and r.status < 300):
                raise CommError(f'{url} {method} returns {r.status}', await r.json())
            return await r.json()
    elif method == 'PUT':
        async with session.put(url, ssl=False, json=payload, headers=headers) as r:
            # print(r.status,r.json())
            if not (r.status >= 200 and r.status < 300):
                raise CommError(f'{url} {method} returns {r.status}', await r.json())
            return await r.json()
    elif method == 'DELETE':
        async with session.delete(url, ssl=False, headers=headers) as r:
            if not (r.status >= 200 and r.status < 300):
                raise CommError(f'{url} {method} returns {r.status}', await r.json())
            return await r.json()
