
from adapay.request_tools import payment_create, payment_query, payment_list, payment_close, request_post, request_get


class Payment(object):

    @classmethod
    def create(cls, **kwargs):
        """
        创建订单
        """
        if not kwargs.get('currency'):
            kwargs['currency'] = 'cny'

        return request_post(payment_create, kwargs)

    @classmethod
    def query(cls, **kwargs):
        """
        支付查询
        """
        url = payment_query.format(payment_id=kwargs.get('payment_id'))
        return request_get(url, kwargs)

    @classmethod
    def list(cls, **kwargs):
        """
        支付查询
        """
        return request_get(payment_list, kwargs)

    @classmethod
    def close(cls, **kwargs):
        """
        关单请求
        """
        url = payment_close.format(payment_id=kwargs['payment_id'])
        return request_post(url, kwargs)
