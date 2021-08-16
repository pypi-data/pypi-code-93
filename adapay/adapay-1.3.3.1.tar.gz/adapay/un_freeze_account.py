from adapay.request_tools import request_post, request_get, un_freeze_account_create, un_freeze_account_query_list


class UnFreezeAccount(object):

    @classmethod
    def create(cls, **kwargs):
        """
        创建账户解冻对象
        """
        return request_post(un_freeze_account_create, kwargs)

    @classmethod
    def list(cls, **kwargs):
        """
        查询账户解冻列表
        """
        return request_get(un_freeze_account_query_list, kwargs)
