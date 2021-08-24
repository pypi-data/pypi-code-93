"""
response.py Response数据整合
By IT小强xqitw.cn <mail@xqitw.cn>
At 1/25/21 5:18 PM
"""


class Response:
    headers = {"X-Frame-Options": "SAMEORIGIN"}

    @classmethod
    def response(
            cls,
            content,
            content_type: str = 'application/json',
            status_code: int = 200,
            headers: dict = None
    ) -> dict:
        """
        返回 response 信息
        :param content:
        :param content_type:
        :param status_code:
        :param headers:
        :return:
        """

        if headers is None:
            headers = {}
        return {
            "content_type": content_type,
            "status_code": status_code,
            'content': content,
            'headers': {**cls.headers, **headers}
        }

    @classmethod
    def acl_error(cls, content: str, status_code: int = 401, content_type: str = '', headers: dict = None):
        return cls.error(content=content, content_type=content_type, status_code=status_code, headers=headers)

    @classmethod
    def error(cls, content: str, status_code: int = 500, content_type: str = '', headers: dict = None):
        return cls.response(content=content, content_type=content_type, status_code=status_code, headers=headers)
