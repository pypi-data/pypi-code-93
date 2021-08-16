from adapay.request_tools import request_post, request_get, checkout_create, checkout_list, page_base_url


class Checkout(object):

    @classmethod
    def create(cls, **kwargs):
        """
        创建收银台对象
        :param kwargs:
        :return:
        """
        return request_post(checkout_create, kwargs, base_url=page_base_url)

    @classmethod
    def list(cls, **kwargs):
        """
        创建收银台对象
        :param kwargs:
        :return:
        """
        return request_get(checkout_list, kwargs, base_url=page_base_url)
