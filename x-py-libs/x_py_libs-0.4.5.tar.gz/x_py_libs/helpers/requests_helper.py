# -*- coding=utf-8 -*-

import requests
import shutil
import os


# PROXY = '127.0.0.1:1081'
# HTTP_PROXY_PORT = ':1080'
HTTP_PROXIES = {
    'http': 'http://127.0.0.1:1081',
    'https': 'http://127.0.0.1:1081'
}
SOCKS_PROXIES = {
    'http': 'socks5://127.0.0.1:1080',
    'https': 'socks5://127.0.0.1:1080'
}

HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3394.0 Safari/537.36',
    # 'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
}


class RequestsHelper(object):

    @staticmethod
    def get(url, params=None):
        return requests.get(url, **({} if params is None else params))

    @staticmethod
    def post(url, **kwargs):
        return requests.post(url, **kwargs)

    @staticmethod
    def fetch_url(url, params=None):
        return requests.get(url, **({} if params is None else params)).content

    @staticmethod
    def fetch_stream(url, return_raw=True):
        response = requests.get(url, stream=True)
        # return requests.get(url, stream=True).content
        if return_raw:
            response.raw.decode_content = True
            return response.raw

        return response

    @staticmethod
    def fetch_page(url, refer_url=None, http_request=None, use_proxy=False, socks_proxy=False, decode_content=False, cookie=None):
        # proxy = '127.0.0.1:1080'
        # proxies = {
        #     'http': 'http://' + proxy,
        #     'https': 'https://' + proxy
        # }

        _headers = HEADERS

        if refer_url is not None:
            _headers['Referer'] = refer_url

        if http_request is not None:
            _headers['x-requested-with'] = http_request

        if cookie is not None:
            _headers['Cookie'] = cookie

        # params = {
        #     'headers': HEADERS
        # }

        # __proxies = HTTP_PROXIES if use_proxy else {}
        _proxies = None
        if use_proxy:
            if not socks_proxy:
                _proxies = HTTP_PROXIES
            else:
                _proxies = SOCKS_PROXIES

        try:
            # r = requests.get(url, **params)
            r = requests.get(url, proxies=_proxies, headers=_headers)
            # r.encoding = 'utf-8'

            if decode_content:
                return r.content.decode('utf-8')

            return r

            # print(r.content.decode('utf-8'))
        except Exception as e:
            print(e)
            return None

    @staticmethod
    def save_fetch(url, save_path):
        rsp = RequestsHelper.fetch_stream(url, return_raw=False)
        # with open(save_path, 'x') as f:
        #     shutil.copyfileobj(raw, f)

        if rsp.status_code == 200:
            with open(save_path, 'wb') as f:
                for chunk in rsp.iter_content(1024):
                    f.write(chunk)

    @staticmethod
    def download(url, save_path, proxies=None, timeout=30, override=False, log_size_lmt=1024, use_proxy=False, socks_proxy=False):

        file_name = url.split("/")[-1].split("?")[0]

        if not os.path.exists(save_path):
            os.makedirs(save_path)

        file_path = os.path.join(save_path, file_name)
        print("Downloading %s from %s.\n" % (file_path, url))

        if os.path.exists(file_path) and not override:
            return

        # if use_proxy:
        #     proxies = HTTP_PROXIES
        # __proxies = None
        if use_proxy:
            if not socks_proxy:
                proxies = HTTP_PROXIES
            else:
                proxies = SOCKS_PROXIES

        try:
            resp = requests.get(url, stream=True, proxies=proxies, timeout=timeout, headers=HEADERS)
            # print(resp.headers)
            if resp.status_code == 404:
                print("File Not Found when retrieve %s.\n" % url)
                raise Exception("404")
            if resp.status_code == 403:
                print("Access Denied when retrieve %s.\n" % url)
                raise Exception("Access Denied")
            # else:
            #     print(resp.status_code)

            # content_length = resp.headers['Content-Length']
            content_length = resp.headers.get('Content-Length')
            # print(type(content_length))
            if content_length is not None:
                # print('content_length:', content_length)
                if int(content_length) <= log_size_lmt:
                    with open(os.path.join(save_path, 's.txt'), 'w+', encoding='utf-8') as f:
                        f.write(url + ' ---------- ' + file_path + ' --------- ' + str(vars(resp)))

            with open(file_path, 'wb') as fh:
                for chunk in resp.iter_content(chunk_size=1024):
                    fh.write(chunk)
        except Exception as err:
            raise err
            print(err)
        # finally:
        #     return file_path
