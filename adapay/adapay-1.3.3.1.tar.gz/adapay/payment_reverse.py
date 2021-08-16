from adapay.request_tools import reverse_create, reverse_query, reverse_query_list, request_post, request_get


class PaymentReverse(object):

    @classmethod
    def create(cls, **kwargs):
        """
        支付撤销
        """
        return request_post(reverse_create, kwargs)

    @classmethod
    def query(cls, **kwargs):
        """
        查询支付撤销
        """
        url = reverse_query.format(reverse_id=kwargs.get('reverse_id'))
        return request_get(url, kwargs)

    @classmethod
    def list(cls, **kwargs):
        """
        查询支付撤销列表
        """
        return request_get(reverse_query_list, kwargs)
