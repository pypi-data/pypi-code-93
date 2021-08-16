from adapay.request_tools import request_get, request_post, confirm_create, confirm_query, confirm_query_list


class PaymentConfrim:

    @classmethod
    def create(cls, **kwargs):
        """
        创建订单确认
        """
        return request_post(confirm_create, kwargs)

    @classmethod
    def query(cls, **kwargs):
        """
        查询订单确认
        """
        url = confirm_query.format(payment_confirm_id=kwargs.get('payment_confirm_id'))
        return request_get(url, kwargs)

    @classmethod
    def list(cls, **kwargs):
        """
         查询订单确认列表
        """
        return request_get(confirm_query_list, kwargs)
