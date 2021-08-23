from collections import OrderedDict


class BaseApi(object):

    def __init__(self, client=None):
        self._client = client

    def _get(self, params):
        return self._client.get(params)

    def _post(self, func_name, params):
        data = OrderedDict()
        data['appkey'] = self._client.appKey
        data['sessionkey'] = self._client.sessionKey
        data['method'] = "{}.{}".format(self.KEY, func_name)
        for i in params.keys():
            data[i] = params[i]
        sign = self._get_sign(data)
        data['sign'] = sign
        return self._client.post(data)

    def _delete(self):
        pass

    def _put(self):
        pass

    def _get_sign(self, params):
        return self._client.encrypt_by_MD5(params)

