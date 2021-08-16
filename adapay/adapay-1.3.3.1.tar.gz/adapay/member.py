from adapay.request_tools import request_post, request_get, member_create, member_query, \
    member_query_list, member_update


class Member(object):

    @classmethod
    def create(cls, **kwargs):
        """
        创建用户
        """
        return request_post(member_create, kwargs)

    @classmethod
    def query(cls, **kwargs):
        """
        查询用户
        """
        url = member_query.format(member_id=kwargs.get('member_id'))
        return request_get(url, kwargs)

    @classmethod
    def list(cls, **kwargs):
        """
        查询用户列表
        """
        return request_get(member_query_list, kwargs)

    @classmethod
    def update(cls, **kwargs):
        """
        更新用户
        """
        return request_post(member_update, kwargs)
