"""

转账对象
"""

from adapay.request_tools import request_get, request_post, transfer_create, list_transfer


class Transfer:

    @classmethod
    def create(cls, **kwargs):
        """
        账户转账
        """
        return request_post(transfer_create, kwargs)

    @classmethod
    def list(cls, **kwargs):
        """
        账户转账列表查询
        """
        return request_get(list_transfer, kwargs)
