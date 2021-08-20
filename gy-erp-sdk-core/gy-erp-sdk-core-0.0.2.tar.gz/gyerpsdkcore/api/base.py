
class BaseApi(object):

    def __init__(self, client=None):
        self._client = client

    def _get(self, **kwargs):
        return self._client.get(**kwargs)

    def _post(self, func_name, **kwargs):
        sign = self._get_sign(func_name, kwargs)
        kwargs['sign'] = sign
        return self._client.post(**kwargs)

    def _delete(self):
        pass

    def _put(self):
        pass

    def _get_sign(self, func_name, params):
        params['appkey'] = self._client.appKey
        params['sessionkey'] = self._client.sessionKey
        params['method'] = "{}.{}".format(self.KEY, func_name)
        return self._client.encrypt_by_MD5(params)

