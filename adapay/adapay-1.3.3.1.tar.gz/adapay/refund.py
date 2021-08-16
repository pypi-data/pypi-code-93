"""

退款接口
"""

from adapay.request_tools import refund_create, refund_query, request_post, request_get


class Refund(object):

    @classmethod
    def create(cls, **kwargs):
        """
        发起退款流程
        """

        url = refund_create.format(id=kwargs.get('id', ''))
        return request_post(url, kwargs)

    @classmethod
    def query(cls, **kwargs):
        """
        退款流程查询
        """

        return request_get(refund_query, kwargs)
