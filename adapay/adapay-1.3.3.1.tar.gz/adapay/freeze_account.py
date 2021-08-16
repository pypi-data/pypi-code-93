from adapay.request_tools import request_post, request_get, freeze_account_create, freeze_account_query_list


class FreezeAccount(object):

    @classmethod
    def create(cls, **kwargs):
        """
        创建账户冻结对象
        """
        return request_post(freeze_account_create, kwargs)

    @classmethod
    def list(cls, **kwargs):
        """
        查询账户冻结列表
        """
        return request_get(freeze_account_query_list, kwargs)
