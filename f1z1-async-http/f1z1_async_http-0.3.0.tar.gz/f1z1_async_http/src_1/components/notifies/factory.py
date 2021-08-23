# @Time     : 2021/7/18
# @Project  : f1z1-g
# @IDE      : PyCharm
# @Author   : Angel
# @Email    : 376355670@qq.com
from operator import not_
from typing import Optional

from ..event_hook import AbstractEventHooksManager, FunctionHooksManager
from .manager import IAsyncNotifierManager, AsyncNotifierManager


class INotifierManagerFactory:

    @classmethod
    def create(cls, hooks: Optional[AbstractEventHooksManager] = None) -> IAsyncNotifierManager:
        raise NotImplementedError("")


class NotifierManagerFactory(INotifierManagerFactory):

    @classmethod
    def create(cls, hooks: Optional[AbstractEventHooksManager] = None):
        return AsyncNotifierManager(cls._get_hooks(hooks))

    @classmethod
    def _get_hooks(cls, hooks: Optional[AbstractEventHooksManager] = None):
        return FunctionHooksManager() if not_(hooks) else hooks
