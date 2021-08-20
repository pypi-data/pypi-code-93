import re
import time
import logging
import requests
import chardet
from pathlib import Path
from .mthreading import ThreadPool
from .dlso import update_attrs

FAIL_ENCODING = 'ISO-8859-1'
DEFAULT_USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'

def get_request_kwargs(useragent, **kwargs):
    """This Wrapper method exists b/c some values in req_kwargs dict
    are methods which need to be called every time we make a request
    """
    kv = kwargs.copy()
    kv['headers'] = kv.get('headers', {'User-Agent': useragent})
    kv['proxies'] = kv.get('proxies', None)
    cb = kv['proxies']
    if callable(cb):
        kv['proxies'] = cb()
    kv['allow_redirects'] = True
    return kv

class MRequest(object):
    """Wrapper for request object for multithreading. If the domain we are
    crawling is under heavy load, the self.resp will be left as None.
    If this is the case, we still want to report the url which has failed
    so (perhaps) we can try again later.
    """
    def __init__(self, url, settings=None, params=None, json=None, data=None, **kwargs):
        self.url = url
        self.settings   = settings
        self.method     = settings.method
        self.useragent  = settings.useragent
        self.params = params
        self.json   = json
        self.data   = data
        self.kwargs = kwargs
        self.resp   = None

    def send(self):
        try:
            self.resp = requests.request(
                self.method, self.url, params=self.params, json=self.json, data=self.data, 
                **get_request_kwargs(self.useragent, **self.kwargs))
            if self.settings.http_success_only:
                self.resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.critical('[zwutils][REQUEST FAILED] ' + str(e))

# pylint: disable=no-member
def multithread_request(urls, settings=None, params_list=None, json_list=None, data_list=None, **kwargs):
    """Request multiple urls via mthreading, order of urls & requests is stable
    returns same requests but with response variables filled.

    thread_timeout: in seconds
    timeout: in seconds, 连接超时设为比3的倍数略大的一个数值
    """
    default_settings = {
        'method': 'get',
        'thread_num': 5,
        'thread_timeout': 6,
        'timeout': 5,
        'useragent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36',
        'cookies': None,
        'proxies': None,
        'http_success_only': True,
    }
    settings = update_attrs(default_settings, settings or {})
    kwargs['timeout'] = kwargs.get('timeout', settings.timeout)
    kwargs['cookies'] = kwargs.get('cookies', settings.cookies)
    kwargs['proxies'] = kwargs.get('proxies', settings.proxies)

    thread_num = settings.thread_num
    timeout = settings.thread_timeout
    pool = ThreadPool(thread_num, timeout)
    m_requests = []
    for i,url in enumerate(urls):
        params  = params_list[i] if params_list and i<len(params_list) else None
        json    = json_list[i] if json_list and i<len(json_list) else None
        data    = data_list[i] if data_list and i<len(data_list) else None
        m_requests.append(MRequest(url, settings, params, json, data, **kwargs))

    for req in m_requests:
        pool.add_task(req.send)

    pool.wait_completion()
    return m_requests


def get_html(url, settings=None, response=None, **kwargs):
    """HTTP response code agnostic
    """
    default_settings = {
        'method': 'get',
        'timeout': 5,
        'useragent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36',
        'cookies': None,
        'proxies': None,
        'http_success_only': True,
        'content_types_ignored': {},
    }
    settings = update_attrs(default_settings, settings or {})
    kwargs['timeout'] = kwargs.get('timeout', settings.timeout)
    kwargs['cookies'] = kwargs.get('cookies', settings.cookies)
    kwargs['proxies'] = kwargs.get('proxies', settings.proxies)
    try:
        return get_html_2XX_only(url, settings, response, **kwargs)
    except requests.exceptions.RequestException as e:
        logging.error('[zwutils] get_html() error. %s on URL: %s', e, url)
        return ''

def get_html_2XX_only(url, settings=None, response=None, **kwargs):
    """We handle error cases:
    - Attempt to find encoding of the html by using HTTP header. Fallback to
      'ISO-8859-1' if not provided.
    - Error out if a non 2XX HTTP response code is returned.
    """
    method = settings.method or 'get'
    useragent = settings.useragent

    if response is not None:
        return _get_html_from_response(response, settings)
    response = requests.request(method, url, **get_request_kwargs(useragent, **kwargs))
    html = _get_html_from_response(response, settings)
    if settings.http_success_only:
        # fail if HTTP sends a non 2XX response
        response.raise_for_status()
    return html

def get_content_2XX_only(url, settings=None, params=None, json=None, data=None, **kwargs):
    resp = requests.request(
        settings.method, url, params=params, json=json, data=data, 
        **get_request_kwargs(settings.useragent, **kwargs))
    rtn = resp.content
    if settings.http_success_only:
        # fail if HTTP sends a non 2XX response
        resp.raise_for_status()
    return rtn

def _get_html_from_response(response, settings=None):
    content_types_ignored = settings.content_types_ignored \
        if hasattr(settings, 'content_types_ignored') else {}
    if response.headers.get('content-type') in content_types_ignored:
        return content_types_ignored[response.headers.get('content-type')]
    if response.encoding != FAIL_ENCODING:
        # return response as a unicode string
        html = response.text
    else:
        html = response.content
        if 'charset' not in response.headers.get('content-type'):
            encodings = requests.utils.get_encodings_from_content(response.text)
            if len(encodings) > 0:
                response.encoding = encodings[0]
                html = response.text
    return html or ''

def downfile(url, settings=None, params=None, json=None, data=None, outpath='.', filename=None, **kwargs):
    default_settings = {
        'method': 'get',
        'timeout': 5,
        'useragent': DEFAULT_USER_AGENT,
        'cookies': None,
        'proxies': None,
        'http_success_only': True,
    }
    settings = update_attrs(default_settings, settings or {})
    kwargs['timeout'] = kwargs.get('timeout', settings.timeout)
    kwargs['cookies'] = kwargs.get('cookies', settings.cookies)
    kwargs['proxies'] = kwargs.get('proxies', settings.proxies)
    kwargs['stream']  = kwargs.get('stream', True)

    resp = requests.request(
        settings.method, url, params=params, json=json, data=data, 
        **get_request_kwargs(settings.useragent, **kwargs))
    if settings.http_success_only:
        # fail if HTTP sends a non 2XX response
        resp.raise_for_status()
    # resp.encoding = resp.apparent_encoding

    outpath = Path(outpath)
    if outpath.is_dir():
        fname = None
        if 'content-disposition' in resp.headers:
            dis = resp.headers['content-disposition']
            arr = re.findall('filename=(.+)', dis)
            fname = arr[0].strip() if len(arr)>0 else None
            if fname:
                # enc = chardet.detect(str.encode(fname))
                # fname = fname.encode().decode('utf-8')
                fname = fname[1:-1] if fname.startswith('"') and fname.endswith('"') else fname
                fname = '%s%s' % ( int(time.time()), fname ) if fname.startswith('.') else fname
        fname = fname or '%s' % int(time.time())
        fname = filename+Path(fname).suffix if filename else fname
        outpath = outpath / fname

    outpath = outpath.resolve()
    with open(str(outpath), 'wb') as f:
        for chunk in resp.iter_content(chunk_size=512 * 1024): 
            # If you have chunk encoded response uncomment if
            # and set chunk_size parameter to None.
            #if chunk: 
            f.write(chunk)
    return outpath

def get_head(url, settings=None, params=None, json=None, data=None, **kwargs):
    default_settings = {
        'method': 'head',
        'timeout': 5,
        'useragent': DEFAULT_USER_AGENT,
        'cookies': None,
        'proxies': None
    }
    settings = update_attrs(default_settings, settings or {})
    kwargs['timeout'] = kwargs.get('timeout', settings.timeout)
    kwargs['cookies'] = kwargs.get('cookies', settings.cookies)
    kwargs['proxies'] = kwargs.get('proxies', settings.proxies)
    kwargs['stream']  = kwargs.get('stream', True)

    resp = requests.request(
        settings.method, url, params=params, json=json, data=data, 
        **get_request_kwargs(settings.useragent, **kwargs))
    return resp

def get_request(url, settings=None, params=None, json=None, data=None, **kwargs):
    default_settings = {
        'method': 'get',
        'timeout': 5,
        'useragent': DEFAULT_USER_AGENT,
        'cookies': None,
        'proxies': None
    }
    settings = update_attrs(default_settings, settings or {})
    kwargs['timeout'] = kwargs.get('timeout', settings.timeout)
    kwargs['cookies'] = kwargs.get('cookies', settings.cookies)
    kwargs['proxies'] = kwargs.get('proxies', settings.proxies)
    kwargs['stream']  = kwargs.get('stream', True)

    resp = requests.request(
        settings.method, url, params=params, json=json, data=data, 
        **get_request_kwargs(settings.useragent, **kwargs))
    return resp

def check_connect(urls):
    rtn = []
    for u in urls:
        r = (u, False)
        try:
            resp = get_head(u)
            status_code = resp.status_code
            if status_code == 200:
                r = (u, True)
            elif status_code == 301 or status_code == 302:
                url = resp.headers['Location']
                r = (url, True)
            elif status_code == 403:
                resp_get = get_request(u)
                if resp_get.status_code == 200:
                    r = (u, True)
        except Exception:
            pass
        rtn.append(r)
    return rtn