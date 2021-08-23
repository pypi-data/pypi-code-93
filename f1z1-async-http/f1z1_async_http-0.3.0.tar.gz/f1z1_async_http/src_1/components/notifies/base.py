# @Time     : 2021/7/18
# @Project  : f1z1-g
# @IDE      : PyCharm
# @Author   : Angel
# @Email    : 376355670@qq.com
from typing import TypeVar

M = TypeVar("M")


class IAsyncNotifier(object):
    """
    异步消息通知器
    """

    async def notify(self, message: M) -> bool:
        raise NotImplementedError("")
