from gyerpsdkcore.api.base import BaseApi


class Trade(BaseApi):
    KEY = "gy.erp.trade"

    def get(self, **kwargs):
        return self._post(
            func_name='get',
            **kwargs
        )

    def add(self, **kwargs):
        return self._post(
            func_name='add',
            **kwargs
        )

    def refund_update(self, **kwargs):
        return self._post(
            func_name='refund.update',
            **kwargs
        )


