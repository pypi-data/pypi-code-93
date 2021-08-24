import urllib.request


class Connection:
    host = ""
    port = 0
    defaultTimeout = 30

    def connect(self):
        request = urllib.request.Request("http://" + self.host + ":" + str(self.port))
        reply = urllib.request.urlopen(request, timeout=self.defaultTimeout)
        if reply.status == 200:
            return True
        return False

    def get(self, path, args="", headers=None, timeout=defaultTimeout):
        if headers is None:
            headers = {'Accept': 'text/plain; charset=UTF-8'}
        request = urllib.request.Request(url="http://" + self.host + ":" + str(self.port) + "/" + path + "?" + args,
                                         headers=headers, method="GET")
        reply = urllib.request.urlopen(request, timeout=timeout)
        return reply

    def post(self, path, data=None, headers=None, timeout=defaultTimeout):
        request = urllib.request.Request(url="http://" + self.host + ":" + str(self.port) + "/" + path, data=data,
                                         headers=headers, method="POST")
        reply = urllib.request.urlopen(request, timeout=timeout)
        return reply



