import asyncio
from applipy import Application, Config, AppHandle
from collections import defaultdict


class CallLogApp(AppHandle):

    N = 0

    def __init__(self, call_logs: dict[int, list[str]]) -> None:
        self.call_log = call_logs[CallLogApp.N]
        self.id = CallLogApp.N
        CallLogApp.N += 1

    async def on_init(self) -> None:
        self.call_log.append('on_init')

    async def on_start(self) -> None:
        self.call_log.append('on_start')

    async def on_shutdown(self) -> None:
        self.call_log.append('on_shutdown')


class ErrorApp(CallLogApp):

    def __init__(self, call_logs: dict[int, list[str]]) -> None:
        super().__init__(call_logs)

    async def on_start(self) -> None:
        await super().on_start()
        if self.id % 2 == 0:
            raise ValueError


class AppBlocking1(CallLogApp):

    def __init__(self, call_logs: dict[int, list[str]]) -> None:
        super().__init__(call_logs)

    async def on_init(self) -> None:
        await super().on_init()
        self.future = asyncio.get_event_loop().create_future()

    async def on_start(self) -> None:
        await super().on_start()
        await self.future

    async def on_shutdown(self) -> None:
        await super().on_shutdown()
        self.future.set_result(None)


class AppBlocking2(CallLogApp):

    def __init__(self, call_logs: dict[int, list[str]]) -> None:
        super().__init__(call_logs)

    async def on_start(self) -> None:
        await super().on_start()
        while True:
            await asyncio.sleep(3600)


class AppBlocking3(CallLogApp):

    def __init__(self, call_logs: dict[int, list[str]]) -> None:
        super().__init__(call_logs)

    async def on_start(self) -> None:
        await super().on_start()
        while True:
            try:
                await asyncio.sleep(3600)
            except asyncio.CancelledError:
                ...


class StopLater(CallLogApp):

    def __init__(self, call_logs: dict[int, list[str]], app: Application) -> None:
        super().__init__(call_logs)
        self.app = app

    async def on_start(self) -> None:
        await super().on_start()
        self.app.stop()


def test_applipy_all_lifecyle_methods_are_called_in_the_right_order() -> None:
    app = Application(Config({}), shutdown_timeout_seconds=1)
    call_logs: dict[int, list[str]] = defaultdict(list)
    app.injector.bind(dict[int, list[str]], call_logs)
    app.register(ErrorApp)
    app.register(ErrorApp)
    app.register(ErrorApp)
    app.register(ErrorApp)

    app.run()

    assert len(call_logs) == 4
    for k in call_logs:
        assert len(call_logs[k]) == 3
        assert call_logs[k] == ['on_init', 'on_start', 'on_shutdown']


def test_applipy_all_lifecyle_methods_are_called_in_the_right_order_after_stop() -> None:
    app = Application(Config({}))
    call_logs: dict[int, list[str]] = defaultdict(list)
    app.injector.bind(dict[int, list[str]], call_logs)
    app.injector.bind(Application, app)
    app.register(AppBlocking1)
    app.register(AppBlocking2)
    app.register(AppBlocking3)
    app.register(StopLater)

    app.run()

    assert len(call_logs) == 4
    for k in call_logs:
        call_log = call_logs[k]
        assert len(call_log) == 3
        assert call_log == ['on_init', 'on_start', 'on_shutdown']
