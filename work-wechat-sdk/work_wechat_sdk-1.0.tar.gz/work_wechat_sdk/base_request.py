import requests


class BaseRequest(object):
    request_url = None
    request_methods_valid = [
        "get", "post", "put", "delete", "head", "options", "patch"
    ]

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.response = None
        self.json_response = None
        self.errmsg = None
        self.call_status = False
        self._request_method = "get"
        self._data = None

    @property
    def data(self):
        self._data = self.kwargs.get("data")
        return self._data

    @data.setter
    def data(self, data):
        self._data = data
        self.kwargs["data"] = data

    @property
    def request_method(self):
        """Mostly, the get method is used to request wanted json data, as a
        result, the property of request_method is set to get by default."""
        return self._request_method

    @request_method.setter
    def request_method(self, method_str):
        request_method_lower = method_str.lower()
        if request_method_lower in self.request_methods_valid:
            self._request_method = request_method_lower
        else:
            raise ValueError(
                "%s is not a valid HTTP request method, please choose one"
                "of %s to perform a normal http request, correct it now."
                "" % (method_str, ",".join(self.request_methods_valid))
            )

    def get_response(self):
        """Get the original response of requests"""
        request = getattr(requests, self.request_method, None)
        if request is None and self._request_method is None:
            raise ValueError("A effective http request method must be set")
        if self.request_url is None:
            raise ValueError(
                "Fatal error occurred, the class property \"request_url\" is"
                "set to None, reset it with an effective url of dingtalk api."
            )
        response = request(self.request_url, **self.kwargs)
        self.response = response
        return response

    def get_json_response(self):
        """This method aims at catching the exception of ValueError, detail:
        http://docs.python-requests.org/zh_CN/latest/user/quickstart.html#json
        """
        self.json_response = self.get_response().json()
        if self.json_response is not None:
            error_code = self.json_response.get("errcode", None)
            self.errmsg = self.json_response.get("errmsg", None)
            self.call_status = True if error_code == 0 else False
        return self.json_response

    def get_call_status(self):
        """The global status of api calling."""
        return self.call_status

    def get_errmsg(self):
        """The errmsg of api calling."""
        return self.errmsg
