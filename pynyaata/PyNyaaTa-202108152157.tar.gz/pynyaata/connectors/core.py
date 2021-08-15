from abc import ABC, abstractmethod
from enum import Enum
from functools import wraps
from json import dumps, loads
from urllib.parse import urlencode

import requests
from requests import RequestException
from redis.exceptions import RedisError

from ..config import CACHE_TIMEOUT, REQUESTS_TIMEOUT, CLOUDPROXY_ENDPOINT, logger, REDIS_ENABLED

if REDIS_ENABLED:
    from ..config import cache

cloudproxy_session = None


class ConnectorReturn(Enum):
    SEARCH = 1
    HISTORY = 2


class ConnectorLang(Enum):
    FR = '🇫🇷'
    JP = '🇯🇵'


class Cache:
    def cache_data(self, f):
        @wraps(f)
        def wrapper(*args, **kwds):
            connector = args[0]
            key = 'pynyaata.%s.%s.%s.%s' % (connector.__class__.__name__, f.__name__, connector.query, connector.page)

            if REDIS_ENABLED:
                json = None

                try:
                    json = cache.get(key)
                except RedisError:
                    pass

                if json:
                    data = loads(json)
                    connector.data = data['data']
                    connector.is_more = data['is_more']
                    connector.on_error = False
                    return

            ret = f(*args, **kwds)

            if not connector.on_error and REDIS_ENABLED:
                try:
                    cache.set(key, dumps({
                        'data': connector.data,
                        'is_more': connector.is_more
                    }), CACHE_TIMEOUT)
                except RedisError:
                    pass

            return ret

        return wrapper


ConnectorCache = Cache()


def curl_content(url, params=None, ajax=False, debug=True):
    from . import get_instance
    output = ''
    http_code = 500
    method = 'post' if (params is not None) else 'get'
    instance = get_instance(url)

    if ajax:
        headers = {'X-Requested-With': 'XMLHttpRequest'}
    else:
        headers = {}

    try:
        if not instance.is_behind_cloudflare:
            if method == 'post':
                response = requests.post(url, params, timeout=REQUESTS_TIMEOUT, headers=headers)
            else:
                response = requests.get(url, timeout=REQUESTS_TIMEOUT, headers=headers)

            output = response.text
            http_code = response.status_code
        elif CLOUDPROXY_ENDPOINT:
            global cloudproxy_session
            if not cloudproxy_session:
                json_session = requests.post(CLOUDPROXY_ENDPOINT, headers=headers, data=dumps({
                    'cmd': 'sessions.create'
                }))
                response_session = loads(json_session.text)
                cloudproxy_session = response_session['session']

            headers['Content-Type'] = 'application/x-www-form-urlencoded' if (method == 'post') else 'application/json'

            json_response = requests.post(CLOUDPROXY_ENDPOINT, headers=headers, data=dumps({
                'cmd': 'request.%s' % method,
                'url': url,
                'session': cloudproxy_session,
                'postData': '%s' % urlencode(params) if (method == 'post') else ''
            }))

            http_code = json_response.status_code
            response = loads(json_response.text)
            if 'solution' in response:
                output = response['solution']['response']

            if http_code == 500:
                requests.post(CLOUDPROXY_ENDPOINT, headers=headers, data=dumps({
                    'cmd': 'sessions.destroy',
                    'session': cloudproxy_session,
                }))
                cloudproxy_session = None
    except RequestException as e:
        if debug:
            logger.exception(e)

    return {'http_code': http_code, 'output': output}


class ConnectorCore(ABC):
    @property
    @abstractmethod
    def color(self):
        pass

    @property
    @abstractmethod
    def title(self):
        pass

    @property
    @abstractmethod
    def favicon(self):
        pass

    @property
    @abstractmethod
    def base_url(self):
        pass

    @property
    @abstractmethod
    def is_light(self):
        pass

    @property
    @abstractmethod
    def is_behind_cloudflare(self):
        pass

    def __init__(self, query, page=1, return_type=ConnectorReturn.SEARCH):
        self.query = query
        self.data = []
        self.is_more = False
        self.on_error = True
        self.page = page
        self.return_type = return_type

    @abstractmethod
    def get_full_search_url(self):
        pass

    @abstractmethod
    def search(self):
        pass

    @abstractmethod
    def get_history(self):
        pass

    @abstractmethod
    def is_vf(self, url):
        pass

    async def run(self):
        if self.on_error:
            if self.return_type is ConnectorReturn.SEARCH:
                self.search()
            elif self.return_type is ConnectorReturn.HISTORY:
                self.get_history()
        return self


class Other(ConnectorCore):
    color = 'is-danger'
    title = 'Other'
    favicon = 'blank.png'
    base_url = ''
    is_light = True
    is_behind_cloudflare = False

    def get_full_search_url(self):
        pass

    def search(self):
        pass

    def get_history(self):
        pass

    def is_vf(self, url):
        return False
