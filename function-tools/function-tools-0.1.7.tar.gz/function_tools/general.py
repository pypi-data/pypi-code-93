from abc import (
    ABCMeta,
    abstractmethod,
)
from collections import (
    deque,
)
from typing import (
    Deque,
    Optional,
)

from django.db import (
    transaction,
)
from django.db.models import (
    Model,
)

from function_tools.mixins import (
    ValidatorMixin,
)
from function_tools.results import (
    BaseRunnableResult,
)
from function_tools.utils import (
    rebind_model_rel_id,
)


class RunnableObject(
    ValidatorMixin,
    metaclass=ABCMeta,
):
    """
    Абстрактный класс для создания классов выполняемых объектов
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._result: Optional[BaseRunnableResult] = None

        self._prepare_result()

    @property
    def result(self) -> BaseRunnableResult:
        return self._result

    def _prepare_result(self):
        """
        Метод подготовки результата
        """
        self._result = BaseRunnableResult()

    @abstractmethod
    def run(self):
        """
        Метод запуска выполняемого объекта
        """


class LazySavingRunnableObject(
    RunnableObject,
    metaclass=ABCMeta,
):
    """
    Абстрактный класс для создания классов с отложенным сохранением

    Функции или другие исполняемые объекты должны иметь возможность быть
    атомарными. Для достижения этой цели необходимо все
    действия по сохранению выполнять в транзакции. Если сохранение
    объектов моделей производится непосредственно в коде, то возникает
    ситуация, когда транзакции становятся длинными. По логике вещей, в
    транзанзакцию должны быть обернуты действия на сохранение объектов. Это
    достигается с помощью предоставляемого функционала. В процессе работы
    функции не производится сохранение объектов модели, а они складываются в
    очередь на сохранение. Создаваемые объекты используются в качестве внешних
    объектов, как и ранее. После выполнения всех действий вызывается метод
    do_save, который открывает транзакцию и выполняет все запланированные на
    выполнение действия в порядке добавления в очередь.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._queue_to_save: Deque = deque()

    def do_on_save(self, object_):
        """
        Метод добавления объекта в очередь на сохранение
        """
        self._queue_to_save.append(object_)

    @abstractmethod
    def _do_save_objects_queue(self):
        """
        Выполенение сохранения объектов из очереди
        """

    def do_save(self):
        """
        Выполнение действий сохранения объектов из очереди в транзакции
        """
        with transaction.atomic(savepoint=False):
            self._do_save_objects_queue()


class LazySavingActionModelRunnableObject(
    LazySavingRunnableObject,
    metaclass=ABCMeta,
):
    """
    Абстрактный для создания классов исполняемых объектов с отложенным
    сохранением, использующих в качестве объектов объекты моделей и функции как
    действия. В обычном случае, функции представляют из себя замыкания.
    """
    def _do_save_objects_queue(self):
        """
        Выполенение сохранения объектов из очереди
        """
        while self._queue_to_save:
            x = self._queue_to_save.popleft()

            if callable(x):
                x()
            else:
                if isinstance(x, Model):
                    rebind_model_rel_id(x)
                    x.save()
