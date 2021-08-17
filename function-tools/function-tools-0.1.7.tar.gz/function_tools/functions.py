from abc import (
    ABCMeta,
    abstractmethod,
)
from collections import (
    Iterable,
    Sequence,
    deque,
)
from typing import (
    Deque,
    Optional,
)

from function_tools.general import (
    LazySavingActionModelRunnableObject,
    RunnableObject,
)
from function_tools.mixins import (
    GlobalHelperMixin,
    HelperMixin,
)


class BaseFunction(
    HelperMixin,
    RunnableObject,
    metaclass=ABCMeta,
):
    """
    Базовый класс для создания функций
    """

    @abstractmethod
    def _prepare(self):
        """
        Метод содержащий все действия работы функции
        """

    def run(self):
        """
        Контрактный метод служащий для запуска функции
        """
        self._prepare()


class LazySavingFunction(
    BaseFunction,
    LazySavingActionModelRunnableObject,
    metaclass=ABCMeta,
):
    """
    Абстрактный класс для создания классов функций с отложенным сохранением
    """

    def __init__(self, *args, ignore_errors_on_saving: bool = False, **kwargs):
        """
        Инициализация функции с отложенным сохранением

        Args:
            ignore_errors_on_saving Указывает на игнорирование наличия ошибок при выполнении запроса и необходимость
            сохранения результата в БД в любом случае
        """
        self._ignore_errors_on_saving = ignore_errors_on_saving

        super().__init__(*args, **kwargs)

    def do_on_save(self, object_):
        """
        Добавление действия на момент сохранения

        Принимает действие (список, экземпляр модели, функция)
        """
        if isinstance(object_, (Iterable, Sequence)):
            for act in object_:
                self.do_on_save(act)
        else:
            self._queue_to_save.append(object_)

    def run(self):
        """
        Выполение действий функции с дальнейшим сохранением объектов в базу
        при отсутствии ошибок или явном указании игнорирования ошибок при сохранении
        """
        self._prepare()

        if self._ignore_errors_on_saving or self.result.has_not_errors:
            self.do_save()


class LazySavingPredefinedQueueFunction(
    LazySavingFunction,
    metaclass=ABCMeta
):
    """
    Базовый класс для создания функций с отложенным сохранением объектов
    моделей с предустрановленной очередью
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._queue: Optional[Deque] = deque()


class LazySavingPredefinedQueueGlobalHelperFunction(
    GlobalHelperMixin,
    LazySavingPredefinedQueueFunction,
    metaclass=ABCMeta
):
    """
    Базовый класс для создания функций с отложенным сохранением,
    предустановленной очередью на сохранение и глобальным помощником
    """


class LazyDelegateSavingPredefinedQueueFunction(
    LazySavingPredefinedQueueFunction,
    metaclass=ABCMeta,
):
    """
    Базовый класс для создания функций с предустановленной очередью
    делегированным пусковику сохранением. В рамках функции производится
    наполнение очереди сохраняемых объектов, но сохранение будет производиться
    на уровне пусковика в открытой транзакции. Это требуется, когда функции
    должны выполняться цепочкой в рамках одной транзакции  для достижения
    атомарности.
    """

    def do_save(self):
        """
        Выполнение сохранения объектов в зависимости от признака глобального
        сохранения создаваемых объектов функции.
        """
        self._do_save_objects_queue()

    def run(self):
        """
        Выполнение действий функции с дальнейшим сохранением объектов в базу
        при отсутствии ошибок и локальном сохранении
        """
        self._prepare()


class LazyDelegateSavingPredefinedQueueGlobalHelperFunction(
    GlobalHelperMixin,
    LazyDelegateSavingPredefinedQueueFunction,
    metaclass=ABCMeta,
):
    """
    Базовый класс для создания функций с отложенным сохранением объектов,
    предустановленной очередью, делегированным сохранением объектов пускателю и
    глобальным помощником
    """


class LazySavingSettableQueueFunction(
    LazySavingFunction,
    metaclass=ABCMeta,
):
    """
    Базовый класс для создания функций с отложенным сохранением объектов с
    устанавливаемой очередью объектов на сохранение
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

    def set_queue_to_save(self, queue_to_save):
        """
        Установка очереди на сохранение
        """
        self._queue_to_save = queue_to_save


class LazySavingSettableQueueGlobalHelperFunction(
    GlobalHelperMixin,
    LazySavingSettableQueueFunction,
    metaclass=ABCMeta,
):
    """
    Базовый класс для создания функций с отложенным сохранением объектов,
    устанавливаемой очередью и глобальным помощником
    """


class LazyDelegateSavingSettableQueueFunction(
    LazySavingSettableQueueFunction,
    metaclass=ABCMeta,
):
    """
    Базовый класс для создания функций с устанавливаемой очередью
    делегированным пусковику сохранением. В рамках функции производится
    наполнение очереди сохраняемых объектов, но сохранение будет производиться
    на уровне пусковика в открытой транзакции. Это требуется, когда функции
    должны выполняться цепочкой в рамках одной транзакции  для достижения
    атомарности. Используется в связке с LazySavingGeneralQueueRunner и его
    наследниками.
    """

    def do_save(self):
        """
        Сохранение делегировано на уровень пусковика
        """

    def run(self):
        """
        Выполнение действий функции с дальнейшим сохранением объектов
        """
        self._prepare()


class LazyDelegateSavingSettableQueueGlobalHelperFunction(
    GlobalHelperMixin,
    LazyDelegateSavingSettableQueueFunction,
    metaclass=ABCMeta,
):
    """
    Базовый класс для создания функций с отложенным сохранением объектов,
    устанавливаемой очередью, делегированным сохранением объектов пускателю и
    глобальным помощником. Используется в связке с LazySavingGeneralQueueRunner.
    """
