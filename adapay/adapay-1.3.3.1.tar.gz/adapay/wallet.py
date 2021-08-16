from adapay.request_tools import request_post, wallet_login, page_base_url


class Wallet(object):

    @classmethod
    def login(cls, **kwargs):
        """
        钱包用户登录
        :param kwargs:
        :return:
        """
        return request_post(wallet_login, kwargs, base_url=page_base_url)
