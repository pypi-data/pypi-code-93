from typing import Type
from applipy import Module as Module_, AppHandle, LoggingModule, BindFunction, RegisterFunction
from asyncio import get_event_loop
from .common import ApplipyProcess
from logging import Logger
from tempfile import NamedTemporaryFile


class App(AppHandle):

    def __init__(self, logger: Logger) -> None:
        self._logger = logger.getChild('test-app')

    async def on_init(self) -> None:
        self._logger.debug("on_init")

    async def on_start(self) -> None:
        self._logger.debug("on_start")
        self.future = get_event_loop().create_future()
        await self.future

    async def on_shutdown(self) -> None:
        self._logger.debug("on_shutdown")
        self.future.set_result(None)


class Module(Module_):

    def configure(self, bind: BindFunction, register: RegisterFunction) -> None:
        register(App)

    @classmethod
    def depends_on(cls) -> tuple[Type[Module_], ...]:
        return LoggingModule,


def test_applipy_process() -> None:
    with NamedTemporaryFile('r') as f:
        with ApplipyProcess('./tests/acceptance', 'test_basic', {'log_file': f.name}) as p:
            pass
        assert p.returncode == 0
        f.seek(0)
        assert [s for s in f.readlines()
                if s.startswith('DEBUG:test_basic.test-app:')] == ['DEBUG:test_basic.test-app:on_init\n',
                                                                   'DEBUG:test_basic.test-app:on_start\n',
                                                                   'DEBUG:test_basic.test-app:on_shutdown\n']
