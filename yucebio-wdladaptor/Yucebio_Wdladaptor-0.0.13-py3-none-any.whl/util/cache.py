
from typing import Callable


class SimpleCache(object):

    def __init__(self, init: dict= {}):
        self._cache = dict(init)

    def __call__(self, key: str, setter_or_default = None):
        if not setter_or_default:
            if key in self._cache:
                return self._cache[key]
            return

        if isinstance(setter_or_default, Callable):
            self._cache[key] = setter_or_default(self)
        else:
            self._cache[key] = setter_or_default
        return self._cache[key]


if __name__ == "__main__":
    cache = SimpleCache({"a": 1})

    # 1. 获取缓存数据
    x = cache('x', default="val x")

    # 2. 获取或设置缓存数据
    cache('y', setter=lambda _: 5)

    # 3. 更新缓存
    z = cache('b')