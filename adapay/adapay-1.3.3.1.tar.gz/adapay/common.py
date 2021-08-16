
from adapay.request_tools import payment_create, payment_query, payment_list, payment_close, request_post, request_get


class AdapayCommon(object):

    @classmethod
    def requestAdapay(cls, **kwargs):
        """
        创建订单
        """
        if not kwargs.get('currency'):
            kwargs['currency'] = 'cny'

        return request_post(payment_create, kwargs)

    @classmethod
    def queryAdapay(cls, **kwargs):
        """
        支付查询
        """
        url = payment_query.format(payment_id=kwargs.get('payment_id'))
        return request_get(url, kwargs)

    @classmethod
    def requestAdapayUits(cls, **kwargs):
        """
        支付查询
        """
        return request_get(payment_list, kwargs)

    @classmethod
    def queryAdapayUits(cls, **kwargs):
        """
        关单请求
        """
        url = payment_close.format(kwargs['payment_id'])
        return request_post(url, kwargs)
