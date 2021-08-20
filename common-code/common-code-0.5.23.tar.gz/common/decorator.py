from concurrent.futures.thread import ThreadPoolExecutor

import requests
from requests.exceptions import ConnectionError as ConnError


def thread_pool_decorator(max_workers=10):
    pool = ThreadPoolExecutor(max_workers=max_workers)

    def external_wrapper(function):
        def internal_wrapper(*args, **kwargs):
            task = pool.submit(function, *args, **kwargs)
            # return task.result()

        return internal_wrapper

    return external_wrapper


METHOD_POST = "POST"
METHOD_GET = "GET"
METHOD_PUT = "PUT"
METHOD_DELETE = "DELETE"

DEFAULT_STOP_CODE = [403, 404, 400, 500]
DEFAULT_SUCCESS_CODE = [200, 201]


def requests_decorator(method=METHOD_GET, success_code=200, stop_code=None, failure_skip=True, max_retry=3, timeout=30):
    def external_wrapper(function):
        def internal_wrapper(*args, **kwargs):
            _method = kwargs.pop("method", None)
            if not _method:
                _method = method
            _method = _method.upper()
            if _method != METHOD_GET and _method != METHOD_POST and _method != METHOD_PUT and _method != METHOD_DELETE:
                raise ValueError(str(_method) + "  request mode is not supported")
            data = kwargs.pop("data", None)
            if data:
                if not isinstance(data, str):
                    raise ValueError("  data type must bu str")

            re_try = 0
            obj = not isinstance(args[0], str)
            url = args[1] if obj else args[0]
            _stop_code = DEFAULT_STOP_CODE
            if stop_code:
                if isinstance(stop_code, list):
                    _stop_code = DEFAULT_STOP_CODE + stop_code
            while re_try < max_retry:
                try:
                    re_try += 1
                    response = requests.request(_method, url, timeout=timeout, **kwargs)

                    if any(
                            [
                                response.status_code == success_code,
                                response.status_code in DEFAULT_SUCCESS_CODE,
                                response.status_code in _stop_code,
                            ]
                    ):
                        break
                except ConnectionError as e:
                    raise ConnectionError(e)
                except ConnError as e:
                    raise ConnError(e)
                except TypeError as e:
                    raise TypeError(e)
                except Exception as e:
                    pass
            else:
                return
            if response.status_code in _stop_code and failure_skip:
                return
            if obj:
                return function(args[0], args[1], response, *args[2:])
            else:
                return function(args[0], response, *args[1:])

        return internal_wrapper

    return external_wrapper


@requests_decorator()
def download(url, *args):
    response = args[0]
    return response
