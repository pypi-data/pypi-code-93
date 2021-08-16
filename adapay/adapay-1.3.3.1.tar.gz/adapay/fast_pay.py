from adapay.request_tools import request_post, request_get, fast_pay_card_bind, fast_pay_card_bind_confirm, \
    fast_pay_card_bind_list, fast_pay_confirm, fast_pay_sms_code, page_base_url


class FastPay(object):

    @classmethod
    def card_bind(cls, **kwargs):
        """
        创建快捷支付绑卡对象
        """
        return request_post(fast_pay_card_bind, kwargs, base_url=page_base_url)

    @classmethod
    def card_bind_list(cls, **kwargs):
        """
        查询快捷支付列表
        """
        return request_get(fast_pay_card_bind_list, kwargs, base_url=page_base_url)

    @classmethod
    def card_bind_confirm(cls, **kwargs):
        """
        快捷支付绑卡确认
        """
        return request_post(fast_pay_card_bind_confirm, kwargs, base_url=page_base_url)

    @classmethod
    def confirm(cls, **kwargs):
        """
        快捷支付确认
        """
        return request_post(fast_pay_confirm, kwargs)

    @classmethod
    def sms_code(cls, **kwargs):
        """
        快捷支付短信重发
        """
        return request_post(fast_pay_sms_code, kwargs)
