import asyncio
import traceback

from typing import (
    Any,
    Callable,
    Coroutine,
    List,
    Optional,
    Set,
    Type,
    TypeVar,
)
from logging import (
    ERROR,
    INFO,
    Logger,
    WARN,
    getLevelName,
)
from asyncio import (
    AbstractEventLoop,
    Task,
)
from applipy_inject import Injector
from applipy.application.apphandle import (
    AppHandle,
    AppHandleProvider,
    RegisterFunction,
)
from applipy.application.module import (
    BindFunction,
    Module,
)
from applipy.config.config import Config


T = TypeVar('T')


class FallbackLogger:

    _injector: Injector
    _config: Config

    def __init__(self, injector: Injector, config: Config) -> None:
        self._injector = injector
        self._config = config

    def log(self, level: int, fmt: str, *args: Any, **kwargs: Any) -> None:
        try:
            self._injector.get(Logger).log(level, fmt, *args, **kwargs)
        except Exception:
            cfg_level = self._config.get('logging.level', INFO)
            if not isinstance(cfg_level, int):
                cfg_level = getLevelName(cfg_level)
            if not isinstance(level, int):
                level = getLevelName(level)
            if level >= cfg_level:
                print(f"[{getLevelName(level)}]", fmt % args)


class ModuleManager(FallbackLogger):

    _modules: Set[Type[Module]]

    def __init__(self, injector: Injector, config: Config) -> None:
        super().__init__(injector, config)
        self._modules = set()

    def install(self, module: Type[Module]) -> 'ModuleManager':
        if module not in self._modules:
            self._modules.add(module)
            self._injector.bind_provider(Module, module)
            for dep in module.depends_on():
                self.install(dep)

        return self

    def configure_all(self, bind_function: BindFunction, register_function: RegisterFunction) -> None:
        instances = self.injector.get_all(Module)
        for instance in instances:
            instance.configure(bind_function, register_function)
            self.log(INFO, f'Installing module `{instance.__class__.__module__}.{instance.__class__.__name__}`')

        self._modules = set()

    @property
    def injector(self) -> Injector:
        return self._injector


async def _wrap_apphandle_coro(coro: Coroutine[Any, Any, None], log: Callable[[int, str], None]) -> None:
    try:
        await coro
    except SystemExit:
        raise
    except Exception:
        log(ERROR, ''.join(traceback.format_exc()))


class AppHandleManager(FallbackLogger):

    def __init__(self, injector: Injector, config: Config) -> None:
        super().__init__(injector, config)

    def register(self,
                 app_handle_provider: AppHandleProvider) -> None:
        self._injector.bind_provider(AppHandle, app_handle_provider)

    async def init_all(self) -> None:
        app_handles = self._injector.get_all(AppHandle)
        tasks = (asyncio.get_event_loop().create_task(_wrap_apphandle_coro(app_handle.on_init(), self.log),
                                                      name=app_handle.__class__.__name__ + '.on_init')
                 for app_handle in app_handles)
        await asyncio.gather(*tasks)

    async def start_all(self) -> None:
        app_handles = self._injector.get_all(AppHandle)
        tasks = (asyncio.get_event_loop().create_task(_wrap_apphandle_coro(app_handle.on_start(), self.log),
                                                      name=app_handle.__class__.__name__ + '.on_start')
                 for app_handle in app_handles)
        await asyncio.gather(*tasks)

    async def shutdown_all(self) -> None:
        app_handles = self._injector.get_all(AppHandle)
        tasks = (asyncio.get_event_loop().create_task(_wrap_apphandle_coro(app_handle.on_shutdown(), self.log),
                                                      name=app_handle.__class__.__name__ + '.on_shutdown')
                 for app_handle in app_handles)
        await asyncio.gather(*tasks)


class Application(FallbackLogger):

    _config: Config
    _shutdown_timeout_seconds: int
    _loop: Optional[AbstractEventLoop]
    _app_handle_manager: AppHandleManager
    _module_manager: ModuleManager
    _running: bool

    def __init__(self,
                 config: Config,
                 shutdown_timeout_seconds: int = 1,
                 injector: Optional[Injector] = None,
                 module_manager: Optional[ModuleManager] = None,
                 app_handle_manager: Optional[AppHandleManager] = None,
                 loop: Optional[AbstractEventLoop] = None) -> None:
        super().__init__(injector or Injector(), config)
        self._config = config
        self._shutdown_timeout_seconds = shutdown_timeout_seconds
        self._loop = loop
        self._app_handle_manager = (app_handle_manager or AppHandleManager(self._injector, config))
        self._module_manager = module_manager or ModuleManager(self._injector, config)
        self._running = False

    def install(self, module: Type[Module]) -> 'Application':
        self._module_manager.install(module)
        return self

    def register(self, app_handle_provider: AppHandleProvider) -> 'Application':
        self._app_handle_manager.register(app_handle_provider)
        return self

    @property
    def injector(self) -> Injector:
        return self._injector

    def run(self) -> None:
        self._loop = self._loop or asyncio.get_event_loop()

        self._injector.bind(Config, self._config)
        self._module_manager.configure_all(
            self._injector.bind,
            self._app_handle_manager.register
        )

        core_tasks = []

        self._running = True
        app_name = self._config.get('app.name', 'applipy')
        core_tasks.append(self._loop.create_task(self._run_app(), name=app_name))
        self._loop.run_forever()
        self._running = False
        core_tasks.append(self._loop.create_task(self._shutdown_app(), name=app_name + '.shutdown_app'))

        core_tasks.append(
            self._loop.create_task(asyncio.wait_for(self._loop.shutdown_asyncgens(), self._shutdown_timeout_seconds),
                                   name=app_name + '.shutdown_asyncgens')
        )
        if hasattr(self._loop, 'shutdown_default_executor'):
            core_tasks.append(
                self._loop.create_task(asyncio.wait_for(self._loop.shutdown_default_executor(),
                                                        self._shutdown_timeout_seconds),
                                       name=app_name + '.shutdown_default_executor')
            )

        self._cancel_loop_tasks(core_tasks)

    def stop(self) -> None:
        if self._loop is not None:
            self._loop.stop()

    async def _run_app(self) -> None:
        try:
            await self._app_handle_manager.init_all()
            await self._app_handle_manager.start_all()
        except asyncio.CancelledError:
            self.log(WARN, traceback.format_exc())
        except Exception:
            self.log(ERROR, traceback.format_exc())
        finally:
            if self._running:
                self.stop()

    async def _shutdown_app(self) -> None:
        try:
            await asyncio.wait_for(self._app_handle_manager.shutdown_all(), self._shutdown_timeout_seconds)
        except asyncio.TimeoutError:
            self.log(ERROR, traceback.format_exc())

    def _cancel_loop_tasks(self, core_tasks: List[Task[None]]) -> None:
        assert self._loop is not None
        core_future = asyncio.gather(*core_tasks)
        try:
            self._loop.run_until_complete(asyncio.wait_for(asyncio.shield(core_future),
                                                           self._shutdown_timeout_seconds))
        except asyncio.TimeoutError:
            for t in (t for t in asyncio.all_tasks(self._loop) if not t.done() and t not in core_tasks):
                t.cancel()
                self.log(WARN, 'Cancelled task %s', t.get_name())
        try:
            self._loop.run_until_complete(asyncio.wait_for(asyncio.shield(core_future),
                                                           self._shutdown_timeout_seconds))
        except asyncio.TimeoutError:
            for t in (t for t in asyncio.all_tasks(self._loop) if not t.done()):
                t.cancel()
                self.log(ERROR, "Task %s didn't finish", t.get_name())
