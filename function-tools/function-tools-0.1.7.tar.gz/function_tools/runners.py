from abc import (
    ABCMeta,
)
from collections import (
    deque,
)
from typing import (
    Deque,
    Optional,
    Union,
)

from function_tools.errors import (
    BaseError,
)
from function_tools.functions import (
    LazyDelegateSavingSettableQueueFunction,
)
from function_tools.general import (
    LazySavingActionModelRunnableObject,
    LazySavingRunnableObject,
    RunnableObject,
)
from function_tools.mixins import (
    GlobalHelperMixin,
    HelperMixin,
)


class BaseRunner(
    HelperMixin,
    RunnableObject,
    metaclass=ABCMeta,
):
    """
    Базовый класс для создания пусковиков выполнения запускаемых объектов
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._queue: Deque[RunnableObject] = deque()

    def _prepare_runnable_before_enqueue(
        self,
        runnable: RunnableObject,
    ):
        """
        Подготовка запускаемого объекта к работе.

        В данной точне расширения можно пропатчить объект через публичные методы
        """
        if isinstance(runnable, GlobalHelperMixin):
            runnable.set_global_helper(
                global_helper=self._helper,
            )

    def enqueue(
        self,
        runnable: RunnableObject,
        *args,
        **kwargs,
    ):
        """
        Добавление задачи на выполнение функции в очередь
        """
        self._prepare_runnable_before_enqueue(
            runnable=runnable,
        )

        self._queue.append(runnable)

    def run(self):
        """
        Выполнение всех задач стоящих в очереди
        """
        self.validate()

        if self.result.has_not_errors:
            while self._queue:
                runnable: RunnableObject = (
                    self._queue.popleft()
                )

                runnable.before_validate()
                runnable.validate()
                runnable.after_validate()

                runnable.run()

                self.result.append_entity(runnable.result)


class LazySavingRunner(
    BaseRunner,
    LazySavingRunnableObject,
    metaclass=ABCMeta,
):
    """
    Абстрактный класс для создания классов пусковиков с отложенным сохранением
    объектов из очередей на сохранение запускаемых объектов.

    Сохранение производится, когда все запускаемые объекты очереди отработают.
    """

    def _do_save_objects_queue(self):
        """
        Запуск сохранения у выполняемых объектов
        """
        while self._queue_to_save:
            runnable: LazySavingRunnableObject = self._queue_to_save.popleft()
            runnable.do_save()

    def run(self):
        """
        Выполнение всех задач стоящих в очереди
        """
        self.validate()

        if self.result.has_not_errors:
            while self._queue:
                runnable: RunnableObject = self._queue.popleft()

                runnable.run()

                self.result.append_entity(runnable.result)

                if runnable.result.has_not_errors:
                    self._queue_to_save.append(runnable)


class LazyStrictSavingRunner(
    LazySavingRunner,
    metaclass=ABCMeta,
):
    """
    Абстрактный класс для создания классов пусковиков с отложенным сохранением
    объектов в строгом режиме.

    Если не все выполняемые объекты отработали корректно, то ни один не
    сохраняется.
    """

    def _get_strict_saving_error(self) -> BaseError:
        """
        Ошибка, которая должна быть возвращена при несоблюдении условий
        строгого режима
        """
        return BaseError()

    def run(self):
        """
        Выполнение всех задач стоящих в очереди
        """
        self.before_validate()
        self.validate()
        self.after_validate()

        if self.result.has_not_errors:
            queue_length = len(self._queue)

            while self._queue:
                runnable: RunnableObject = (
                    self._queue.popleft()
                )
                runnable.run()

                self.result.append_entity(runnable.result)

                if runnable.result.has_not_errors:
                    self._queue_to_save.append(runnable)

            if queue_length != len(self._queue_to_save):
                self.result.append_entity(
                    self._get_strict_saving_error()
                )

                self._queue_to_save.clear()


class GlobalHelperRunner(
    GlobalHelperMixin,
    BaseRunner,
    metaclass=ABCMeta,
):
    """
    Базовый класс для создания пусковиков выполнения запускаемых объектов с
    глобальным помощником
    """


class LazySavingGlobalHelperRunner(
    GlobalHelperMixin,
    LazySavingRunner,
    metaclass=ABCMeta,
):
    """
    Абстрактный класс для создания классов пусковиков с отложенным сохранением
    объектов с глобальным помощником
    """


class LazyStrictSavingGlobalHelperRunner(
    GlobalHelperMixin,
    LazyStrictSavingRunner,
    metaclass=ABCMeta,
):
    """
    Абстрактный класс для создания классов пусковиков с отложенным сохранением
    объектов в строгом режиме c глобальным помощником
    """


class LazySavingSettableQueueRunner(
    BaseRunner,
    LazySavingRunnableObject,
    metaclass=ABCMeta,
):
    """
    Абстрактный класс для создания пусковиков с устанавливаемой очередью на
    сохранение.
    """

    def __init__(
        self,
        *args,
        queue_to_save: Optional[Deque] = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        # очередь содержащая объекты на сохранение
        self._queue_to_save: Optional[Deque] = queue_to_save

    def set_queue(self, queue_to_save):
        """
        Установка очереди на сохранение
        """
        self._queue_to_save = queue_to_save

    def _prepare_runnable_before_enqueue(
        self,
        runnable: Union['LazySavingSettableQueueRunner', LazyDelegateSavingSettableQueueFunction],  # noqa
    ):
        runnable.set_queue_to_save(
            queue_to_save=self._queue_to_save,
        )


class LazyDelegateSavingSettableQueueRunner(
    LazySavingSettableQueueRunner,
    metaclass=ABCMeta,
):
    """
    Абстрактный класс для создания пусковиков с устанавливаемой очередью на
    сохранение. Используется в связке с LazySavingGeneralQueueRunner в качестве
    пусковкика. В качестве запускаемых объектов используются
    LazyDelegateSavingSettableQueueFunction и его потомки, и объекты самого
    класса и его потомков.
    """

    def do_save(self):
        """
        Сохранение делегировано пусковику
        """


class LazySavingGeneralQueueRunner(
    BaseRunner,
    LazySavingActionModelRunnableObject,
    metaclass=ABCMeta,
):
    """
    Абстрактный класс для создания пусковиков с единой очередью сохранения для
    всех исполняемых объектов. Используется в паре
    LazyDelegateSavingSettableQueueFunction,
    LazyDelegateSavingSettableQueueRunner и их наследниками.
    """

    def _prepare_runnable_before_enqueue(
        self,
        runnable: Union['LazyDelegateSavingSettableQueueRunner', LazyDelegateSavingSettableQueueFunction],  # noqa
    ):
        runnable.set_queue_to_save(
            queue_to_save=self._queue_to_save,
        )
