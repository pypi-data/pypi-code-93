# @Time     : 2021/8/20
# @Project  : f1z1-g
# @IDE      : PyCharm
# @Author   : Angel
# @Email    : 376355670@qq.com
from abc import abstractmethod
from operator import lt, not_

from .hook import AFuncs, Hook


class NotificationCounter:

    @abstractmethod
    def increment(self, message):
        pass

    @abstractmethod
    def decrement(self, message):
        pass

    @abstractmethod
    def clear(self):
        pass

    @property
    @abstractmethod
    def count(self) -> int:
        pass


class Notification_:
    __slots__ = "_message"

    @abstractmethod
    async def notify(self, hook: AFuncs):
        pass


class Notifier:

    @abstractmethod
    async def handle(self, message):
        pass

    def to_list(self):
        return [self.handle]


class NumCounter(NotificationCounter):

    def __init__(self):
        self._count = 0

    @property
    def count(self):
        return self._count

    def increment(self, message):
        self._count += 1

    def decrement(self, message):
        self._count -= 1
        if self._lt_zero():
            self.clear()

    def clear(self):
        self._count = 0

    def _lt_zero(self):
        return lt(self._count, 0)


class Notification(Notification_):

    def __init__(self, message):
        self._message = message

    async def notify(self, hook: AFuncs):
        for _, fn in enumerate(hook):
            await fn(self._message)

    def __str__(self):
        return f"{self.__class__.__name__}(message={self._message})"


class REQNotifier(Notifier):

    def __init__(self, counter: NotificationCounter, hook: Hook = None):
        self._counter = counter
        self._hook = hook if not_(hook) else hook.request

    async def handle(self, message):
        self.update(message)
        await self.notification(message)

    def update(self, message):
        self._counter.increment(message)

    async def notification(self, message):
        if not_(self._hook):
            return
        await Notification(message).notify(self._hook)


class RESPNotifier(Notifier):
    COMPLETED = 0

    def __init__(self, counter: NotificationCounter, hook: Hook = None):
        self._counter = counter
        self._hook = None if not_(hook) else hook.response

    async def handle(self, message):
        self.update(message)
        await self.notification(message)

    def update(self, message):
        self._counter.decrement(message)

    async def notification(self, message):
        if not_(self._hook):
            return
        await Notification(message).notify(self._hook)
