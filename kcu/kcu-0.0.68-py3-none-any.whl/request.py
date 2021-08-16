from typing import Dict, Optional, Any, List
import time, requests, os
from enum import Enum
from simple_multiprocessing import MultiProcess, Task

from fake_useragent import FakeUserAgent

Response = requests.Response

def download(
    url: str,
    path: str,
    max_request_try_count: int = 3,
    sleep_time: float = 2.5,
    debug: bool = False
) -> bool:
    current_try_count = 0

    while current_try_count < max_request_try_count:
        current_try_count += 1

        if debug:
            print(url + ' | ' + str(current_try_count) + '/' + str(max_request_try_count))

        res = __download(
            url,
            path,
            debug=debug
        )

        if res:
            return True

        time.sleep(sleep_time)

    return False

def __download(
    url: str,
    path: str,
    debug: bool = False
) -> bool:
    import urllib

    try:
        urllib.request.urlretrieve(url, path)

        return os.path.exists(path)
    except Exception as e1:
        if debug:
            print(e1)

        try:
            os.remove(path)
        except Exception as e2:
            if debug:
                print(e2)

        return False

def req_multi_download(
    urls_paths: Optional[Dict[str, str]] = None,
    headers: Optional[Dict] = None,
    max_request_try_count: int = 3,
    sleep_time: float = 2.5,
    debug: bool = False,
    user_agent: Optional[str] = None,
    fake_useragent: bool = False,
    proxy: Optional[str] = None,
    proxy_http: Optional[str] = None,
    proxy_https: Optional[str] = None,
    proxy_ftp: Optional[str] = None,
    allow_redirects: bool = True,
    max_concurent_processes: Optional[int] = None,
    request_timeout: Optional[float] = None
) -> List[bool]:
    mp = MultiProcess()

    for url, path in urls_paths.items():
        mp.tasks.append(
            Task(
                req_download,
                url,
                path,
                headers=headers,
                max_request_try_count=max_request_try_count,
                user_agent=user_agent,
                sleep_time=sleep_time,
                debug=debug,
                proxy=proxy,
                fake_useragent=fake_useragent,
                proxy_http=proxy_http,
                proxy_https=proxy_https,
                proxy_ftp=proxy_ftp,
                allow_redirects=allow_redirects,
                timeout=request_timeout
            )
        )

    return mp.solve(max_concurent_processes=max_concurent_processes)

def req_download(
    url: str,
    path: str,
    headers: Optional[Dict] = None,
    max_request_try_count: int = 3,
    sleep_time: float = 2.5,
    debug: bool = False,
    user_agent: Optional[str] = None,
    fake_useragent: bool = False,
    proxy: Optional[str] = None,
    proxy_http: Optional[str] = None,
    proxy_https: Optional[str] = None,
    proxy_ftp: Optional[str] = None,
    allow_redirects: bool = True,
    timeout: Optional[float] = None
) -> bool:
    current_try_count = 0

    while current_try_count < max_request_try_count:
        current_try_count += 1

        if debug:
            print(url + ' | ' + str(current_try_count) + '/' + str(max_request_try_count))

        res = __req_download(
            url,
            path,
            debug=debug,
            user_agent=user_agent,
            fake_useragent=fake_useragent,
            proxy=proxy,
            proxy_http=proxy_http,
            proxy_https=proxy_https,
            proxy_ftp=proxy_ftp,
            allow_redirects=allow_redirects,
            timeout=timeout
        )

        if res:
            return True

        time.sleep(sleep_time)

    return False

def __req_download(
    url: str,
    path: str,
    debug: bool = False,
    headers: Optional[Dict] = None,
    user_agent: Optional[str] = None,
    fake_useragent: bool = False,
    proxy: Optional[str] = None,
    proxy_http: Optional[str] = None,
    proxy_https: Optional[str] = None,
    proxy_ftp: Optional[str] = None,
    allow_redirects: bool = True,
    timeout: Optional[float] = None
) -> bool:
    headers = headers or {}

    if user_agent or fake_useragent:
        headers = __headers_by_optionally_setting(headers, {'User-Agent':user_agent or FakeUserAgent().random})

    proxies = None

    if proxy or proxy_http or proxy_https or proxy_ftp:
        proxies = {}

        if proxy_http:
            proxies['http'] = proxy_http or proxy

        if proxy_https:
            proxies['https'] = proxy_https or proxy

        if proxy_ftp:
            proxies['ftp'] = proxy_ftp or proxy

    try:
        resp = requests.get(url, headers=headers, proxies=proxies, stream=True, timeout=timeout)

        if resp and resp.status_code in [200, 201]:
            with open(path, 'wb') as f:
                for chunk in resp.iter_content(1024):
                    f.write(chunk)

                return True
    except Exception as e:
        if debug:
            print(e)

    return False

class RequestMethod(Enum):
    GET     = 'GET'
    POST    = 'POST'
    PUT     = 'PUT'
    DELETE  = 'DELETE'

def request(
    url: str,
    method: RequestMethod = RequestMethod.GET,
    params: Optional[Dict] = None,
    headers: Optional[Dict] = None,
    data: Optional[Any] = None,
    max_request_try_count: int = 10,
    sleep_time: float = 2.5,
    debug: bool = False,
    user_agent: Optional[str] = None,
    fake_useragent: bool = False,
    proxy: Optional[str] = None,
    proxy_http: Optional[str] = None,
    proxy_https: Optional[str] = None,
    proxy_ftp: Optional[str] = None,
    allow_redirects: bool = True
) -> Optional[Response]:
    current_try_count = 0

    while current_try_count < max_request_try_count:
        current_try_count += 1

        if debug:
            print(url + ' | ' + str(current_try_count) + '/' + str(max_request_try_count))

        resp = __request(
            url, method,
            params=params,
            headers=headers,
            data=data,
            debug=debug,
            user_agent=user_agent,
            fake_useragent=fake_useragent,
            proxy=proxy,
            proxy_http=proxy_http,
            proxy_https=proxy_https,
            proxy_ftp=proxy_ftp,
            allow_redirects=allow_redirects
        )

        if resp is not None:
            return resp

        if current_try_count >= max_request_try_count:
            break

        time.sleep(sleep_time)

    return None

def get(
    url: str,
    params: Optional[Dict] = None,
    headers: Optional[Dict] = None,
    max_request_try_count: int = 10,
    sleep_time: float = 2.5,
    debug: bool = False,
    user_agent: Optional[str] = None,
    fake_useragent: bool = False,
    proxy: Optional[str] = None,
    proxy_http: Optional[str] = None,
    proxy_https: Optional[str] = None,
    proxy_ftp: Optional[str] = None,
    allow_redirects: bool = True
) -> Optional[Response]:
    return request(url, method=RequestMethod.GET, params=params, headers=headers, max_request_try_count=max_request_try_count, sleep_time=sleep_time, debug=debug, user_agent=user_agent, fake_useragent=fake_useragent, proxy=proxy, proxy_http=proxy_http, proxy_https=proxy_https, proxy_ftp=proxy_ftp,
    allow_redirects=allow_redirects)

def post(
    url: str,
    params: Optional[Dict] = None,
    headers: Optional[Dict] = None,
    data: Optional[Any] = None,
    max_request_try_count: int = 10,
    sleep_time: float = 2.5,
    debug: bool = False,
    user_agent: Optional[str] = None,
    fake_useragent: bool = False,
    proxy: Optional[str] = None,
    proxy_http: Optional[str] = None,
    proxy_https: Optional[str] = None,
    proxy_ftp: Optional[str] = None,
    allow_redirects: bool = True
) -> Optional[Response]:
    return request(url, method=RequestMethod.POST, params=params, headers=headers, data=data, max_request_try_count=max_request_try_count, sleep_time=sleep_time, debug=debug, user_agent=user_agent, fake_useragent=fake_useragent, proxy=proxy, proxy_http=proxy_http, proxy_https=proxy_https, proxy_ftp=proxy_ftp,
    allow_redirects=allow_redirects)

def put(
    url: str,
    params: Optional[Dict] = None,
    headers: Optional[Dict] = None,
    data: Optional[Any] = None,
    max_request_try_count: int = 10,
    sleep_time: float = 2.5,
    debug: bool = False,
    user_agent: Optional[str] = None,
    fake_useragent: bool = False,
    proxy: Optional[str] = None,
    proxy_http: Optional[str] = None,
    proxy_https: Optional[str] = None,
    proxy_ftp: Optional[str] = None,
    allow_redirects: bool = True
) -> Optional[Response]:
    return request(url, method=RequestMethod.PUT, params=params, headers=headers, data=data, max_request_try_count=max_request_try_count, sleep_time=sleep_time, debug=debug, user_agent=user_agent, fake_useragent=fake_useragent, proxy=proxy, proxy_http=proxy_http, proxy_https=proxy_https, proxy_ftp=proxy_ftp,
    allow_redirects=allow_redirects)

def delete(
    url: str,
    params: Optional[Dict] = None,
    headers: Optional[Dict] = None,
    data: Optional[Any] = None,
    max_request_try_count: int = 10,
    sleep_time: float = 2.5,
    debug: bool = False,
    user_agent: Optional[str] = None,
    fake_useragent: bool = False,
    proxy: Optional[str] = None,
    proxy_http: Optional[str] = None,
    proxy_https: Optional[str] = None,
    proxy_ftp: Optional[str] = None,
    allow_redirects: bool = True
) -> Optional[Response]:
    return request(url, method=RequestMethod.DELETE, params=params, headers=headers, data=data, max_request_try_count=max_request_try_count, sleep_time=sleep_time, debug=debug, user_agent=user_agent, fake_useragent=fake_useragent, proxy=proxy, proxy_http=proxy_http, proxy_https=proxy_https, proxy_ftp=proxy_ftp,
    allow_redirects=allow_redirects)

def proxy_to_dict(
    proxy: Optional[str] = None,
    proxy_http: Optional[str] = None,
    proxy_https: Optional[str] = None,
    proxy_ftp: Optional[str] = None
) -> dict:
    proxy_http  = proxy_http  or (proxy if (proxy and not proxy.startswith('https') and not proxy.startswith('ftp'))   else None)
    proxy_https = proxy_https or (proxy if (proxy and not proxy.startswith('http')  and not proxy.startswith('ftp'))   else None)
    proxy_ftp   = proxy_ftp   or (proxy if (proxy and not proxy.startswith('http')  and not proxy.startswith('https')) else None)

    proxy_dict = {}

    if proxy_http:
        proxy_dict['http'] = 'http://{}'.format(proxy_http.split('://')[-1])

    if proxy_https:
        proxy_dict['https'] = 'https://{}'.format(proxy_https.split('://')[-1])

    if proxy_ftp:
        proxy_dict['ftp'] = 'ftp://{}'.format(proxy_ftp.split('://')[-1])

    return proxy_dict

def __request(
    url: str,
    method: RequestMethod,
    params: Optional[Dict] = None,
    headers: Optional[Dict] = None,
    data: Optional[Any] = None,
    debug: bool = False,
    user_agent: Optional[str] = None,
    fake_useragent: bool = False,
    proxy: Optional[str] = None,
    proxy_http: Optional[str] = None,
    proxy_https: Optional[str] = None,
    proxy_ftp: Optional[str] = None,
    allow_redirects: bool = True
) -> Optional[Response]:
    if headers is None:
        headers = {}

    if user_agent or fake_useragent:
        headers = __headers_by_optionally_setting(
            headers,
            {
                'User-Agent':user_agent or FakeUserAgent().random,
                'Accept':'*/*',
                'Cache-Control':'no-cache',
                'Accept-Encoding':'gzip, deflate, br',
                'Connection':'keep-alive'
            }
        )

    proxies = proxy_to_dict(
        proxy=proxy,
        proxy_http=proxy_http,
        proxy_https=proxy_https,
        proxy_ftp=proxy_ftp
    )

    params = {k:v for k, v in params.items() if k and v is not None} if params else None
    headers = {
        k if isinstance(k, str) or isinstance(k, bytes) else str(k):v if isinstance(v, str) or isinstance(v, bytes) else str(v)
        for k, v in headers.items()
    }

    verify = proxies=={}

    if not verify:
        requests.packages.urllib3.disable_warnings()

    request_common_kwargs = {
        'params': params,
        'headers': headers,
        'proxies': proxies,
        'verify': verify,
        'allow_redirects': allow_redirects
    }

    try:
        if method == RequestMethod.GET:
            resp = requests.get(url, **request_common_kwargs)
        elif method == RequestMethod.POST:
            if type(data) == dict or type(data) == list:
                resp = requests.post(url, json=data, **request_common_kwargs)
            else:
                resp = requests.post(url, data=data, **request_common_kwargs)
        else:#elif method == RequestMethod.DELETE:
            resp = requests.post(url, data=data, **request_common_kwargs)

        if resp is None:
            if debug:
                print('Response is None')
        elif resp.status_code >= 400:
            if debug:
                print(resp.status_code, resp.text)

            # return None

        return resp
    except Exception as e:
        if debug:
            print('ERROR:', e)

        return None

def __headers_by_optionally_setting(
    headers: Dict,
    keys_values: Dict
) -> Dict:
    for key, value in keys_values.items():
        if key not in headers:
            headers[key] = value

    return headers