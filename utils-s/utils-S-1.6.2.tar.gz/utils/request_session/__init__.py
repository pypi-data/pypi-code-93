import requests
class requests_session:
    def __init__(self, optional_func=None):
        self.ses = requests.Session()
        self.function = optional_func

    def get(self, url, Head=None):
        response = self.ses.get(url, headers=Head)
        if not self.function is None:
            self.function(response)

        return response

    def post(self, url, data=None, json=None, headers=None):
        request = self.ses.post(url=url, data=data, json=json, headers=headers)
        if self.function is not None:
            self.function(request)

        return request

    def session(self):
        return self.ses


    def request(self, method, url, params=None, data=None, headers=None,
            cookies=None, files=None, auth=None, timeout=None,
            allow_redirects=True, proxies=None,
            hooks=None,verify=None,
            json=None):

        request = self.ses.request(url=url,method=method, proxies=proxies,
                                params=params, data=data, headers=headers,
                                cookies=cookies, files=files, auth=auth, timeout=timeout,
                                allow_redirects=allow_redirects, hooks=hooks, verify=verify, json=json)

        if self.function is not None:
            self.function(request)

        return request

    def change_optional_func(self, function):
        self.function = function


def waste():
    pass