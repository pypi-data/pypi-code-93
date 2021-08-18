import requests
import json
from picsellia.pxl_utils import check_status_code
import picsellia.pxl_exceptions as exceptions


class pxl_requests:

    def __init__(self, headers) -> None:
        self.headers = headers

    def get(self, url: str, data: dict=None, headers: dict=None, verbose=True):
        if headers is not None:
            self.headers = headers
        else:
            headers = self.headers
        try:
            r = requests.get(url=url, data=data, headers=headers)
        except Exception:  # pragma: no cover
            raise exceptions.NetworkError("Server is not responding, please check your host or Picsell.ia server status on twitter")
        check_status_code(r, verbose=verbose)
        return r
    
    def post(self, url: str, data: dict=None, headers: dict=None, verbose=True):
        if headers is not None:
            self.headers = headers
        else:
            headers = self.headers
        try:
            r = requests.post(url=url, data=data, headers=headers)
        except Exception:  # pragma: no cover
            raise exceptions.NetworkError("Server is not responding, please check your host or Picsell.ia server status on twitter")
        check_status_code(r, verbose=verbose)
        return r

    def put(self, url: str, data: dict=None, headers: dict=None, verbose=True):
        if headers is not None:
            self.headers = headers
        else:
            headers = self.headers
        try:
            r = requests.put(url=url, data=data, headers=headers)
        except Exception:  # pragma: no cover
            raise exceptions.NetworkError("Server is not responding, please check your host or Picsell.ia server status on twitter")
        check_status_code(r, verbose=verbose)
        return r
    
    def patch(self, url: str, data: dict=None, headers: dict=None, verbose=True):
        if headers is not None:
            self.headers = headers
        else:
            headers = self.headers
        try:
            r = requests.patch(url=url, data=data, headers=headers)
        except Exception:  # pragma: no cover
            raise exceptions.NetworkError("Server is not responding, please check your host or Picsell.ia server status on twitter")
        check_status_code(r, verbose=verbose)
        return r
    
    def delete(self, url: str, data: dict=None, headers: dict=None, verbose=True):
        if headers is not None:
            self.headers = headers
        else:
            headers = self.headers
        try:
            r = requests.delete(url=url, data=data, headers=headers)
        except Exception:  # pragma: no cover
            raise exceptions.NetworkError("Server is not responding, please check your host or Picsell.ia server status on twitter")
        check_status_code(r, verbose=verbose)
        return r