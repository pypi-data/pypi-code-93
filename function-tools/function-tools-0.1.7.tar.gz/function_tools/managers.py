from abc import (
    ABCMeta,
    abstractmethod,
)
from typing import (
    Optional,
)

from function_tools.runners import (
    BaseRunner,
)


class RunnerManager(metaclass=ABCMeta):
    """
    Абстрактный класс для создания менеджеров пусковиков запускаемых объектов.
    Служит для добавления функций-задач, пусковиков в очередь на исполнение.
    Является удобным механизмом для скрытия заполнения пусковика и его запуск.
    """
    def __init__(
        self,
        *args,
        **kwargs,
    ):
        self._runner: Optional[BaseRunner] = None

    @abstractmethod
    def _create_runner(self):
        """
        Метод создания пусковика
        """

    @property
    def result(self):
        return self._runner.result

    @abstractmethod
    def _prepare_runner(self):
        """
        Метод подготовки пусковика к запуску

        Чаще всего используется для создания задач и заполнения ими очереди
        пусковика
        """

    def _start_runner(self):
        """
        Точка расширения в месте запуска пусковика
        """
        if self._runner:
            self._runner.run()

    def run(self):
        self._create_runner()
        self._prepare_runner()
        self._start_runner()


class LazySavingRunnerManager(RunnerManager):
    """
    Абстрактный класс для создания менеджеров пусковиков c отложенным
    сохранением. В качестве пусковика должен использоваться потомок
    LazySavingRunner.
    """

    def _do_save(self):
        """
        Запуск сохранения у пусковика
        """
        self._runner.do_save()

    def run(self):
        super().run()
        self._do_save()
