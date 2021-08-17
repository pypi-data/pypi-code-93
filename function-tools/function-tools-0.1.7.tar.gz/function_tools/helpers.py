from typing import (
    Optional,
    Union,
)

from function_tools.caches import (
    BaseCache,
    CacheStorage,
)


class BaseHelper:
    """
    Базовый класс помощника. Предполагается, что у наследников будут
    создаваться кеши и собираться прочая вспомогательная информация, которая
    требуется для исполнения действий
    """
    def __init__(self, *args, **kwargs):
        self.cache: Optional[CacheStorage, BaseCache] = None

        self._create_cache()

    def _create_cache(self):
        """
        Метод создания кеша.

        Кеш хранится в публичном свойстве cache. По умолчанию добавлена
        заглушка.
        """
        self.cache: Union[CacheStorage, BaseCache] = BaseCache()


class BaseRunnerHelper(BaseHelper):
    """
    Базовый класс помощника пусковика выполнения функций
    """


class BaseFunctionHelper(BaseHelper):
    """
    Базовый класс помощника функции. Предполагается, что в наследниках будут
    создаваться кеши и собираться прочая вспомогательная информация, которая
    требуется для исполнения функции
    """
    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

