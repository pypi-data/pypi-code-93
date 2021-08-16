class Proxy:
    def __init__(self, proxy_pool: list = None):
        if not proxy_pool:
            proxy_pool = ['']
        self._proxy_pool = proxy_pool
        self.bad_proxies = []

    @property
    def proxy_pool(self):
        return self._proxy_pool

    @proxy_pool.setter
    def proxy_pool(self, value):
        self._proxy_pool = value

    @property
    def using_proxy(self):
        return self.get_proxy_point()

    def get_proxy_point(self):
        proxy_point = ''
        for proxy_point in self._proxy_pool:
            if proxy_point in self.bad_proxies:
                continue
        if proxy_point:
            return {"https": "https://" + proxy_point, 'http': "http://" + proxy_point }
        else:
            return None





