from gyerpsdkcore.api.base import BaseApi


class Trade(BaseApi):
    KEY = "gy.erp.trade"

    def get(self, params):
        return self._post(
            func_name='get',
            params=params
        )

    def add(self, params):
        return self._post(
            func_name='add',
            params=params
        )

    def refund_update(self, params):
        return self._post(
            func_name='refund.update',
            params=params
        )


