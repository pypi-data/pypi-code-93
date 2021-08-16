from adapay.request_tools import request_post, request_get, cash_draw_create, cash_draw_status


class Drawcash(object):

    @classmethod
    def create(cls, **kwargs):
        """
        取现
        """
        return request_post(cash_draw_create, kwargs)

    @classmethod
    def query(cls, **kwargs):
        """
        取现状态查询
        """
        return request_get(cash_draw_status, kwargs)
