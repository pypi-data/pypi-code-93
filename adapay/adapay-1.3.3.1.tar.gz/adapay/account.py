from adapay.request_tools import request_post, account_pay, page_base_url


class Account(object):

    @classmethod
    def payment(cls, **kwargs):
        """
        创建钱包支付对象
        """
        return request_post(account_pay, kwargs, base_url=page_base_url)
