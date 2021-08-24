# -*- coding: utf-8 -*-

import os
import asyncio

from hagworm import hagworm_slogan
from hagworm import __version__ as hagworm_version

from hagworm.extend.base import catch_error
from hagworm.extend.process import fork_processes
from hagworm.extend.asyncio.base import install_uvloop, Utils, AsyncCirculator
from hagworm.extend.asyncio.buffer import DataAsyncQueue
from hagworm.extend.logging import DEFAULT_LOG_FILE_ROTATOR
from hagworm.extend.interface import FunctorInterface, RunnableInterface
from hagworm.extend.asyncio.zmq import Push, Pull


SIGNAL_PROTOCOL = r'tcp'
SIGNAL_PORT_1 = 0x310
SIGNAL_PORT_2 = 0x601


class Daemon(FunctorInterface):

    def __init__(self):

        self._pids = None

    def _check_pids(self):

        for pid in self._pids.copy():
            if os.waitpid(pid, os.WNOHANG)[0] == pid:
                self._pids.remove(pid)

        return len(self._pids) == 0

    async def _run(self):

        async for _ in AsyncCirculator():
            if self._check_pids():
                break

    def __call__(self, pids):

        self._pids = set(pids)

        Utils.run_until_complete(self._run())


_DEFAULT_DAEMON = Daemon()


class MainProcessAbstract(Daemon, DataAsyncQueue):

    def __init__(self):

        Daemon.__init__(self)
        DataAsyncQueue.__init__(self)

        global SIGNAL_PROTOCOL, SIGNAL_PORT_1, SIGNAL_PORT_2

        self._push_server = Push(f'{SIGNAL_PROTOCOL}://*:{SIGNAL_PORT_1}', True)
        self._pull_server = Pull(f'{SIGNAL_PROTOCOL}://*:{SIGNAL_PORT_2}', True)

    def __call__(self, pids):

        self._push_server.open()
        self._pull_server.open()

        with catch_error():
            super().__call__(pids)

        self._push_server.close()
        self._pull_server.close()

    async def _handle_data(self, data):
        raise NotImplementedError()


class ChildProcessAbstract(FunctorInterface):

    def __init__(self):

        global SIGNAL_PROTOCOL, SIGNAL_PORT_1, SIGNAL_PORT_2

        self._push_client = Push(f'{SIGNAL_PROTOCOL}://localhost:{SIGNAL_PORT_2}')
        self._pull_client = Pull(f'{SIGNAL_PROTOCOL}://localhost:{SIGNAL_PORT_1}')

        self._process_id = None

    async def __call__(self, process_id):

        self._process_id = process_id

        self._push_client.open()
        self._pull_client.open()

        with catch_error():
            await self._run()

        self._push_client.close()
        self._pull_client.close()

    async def _run(self):
        raise NotImplementedError()


class Launcher(RunnableInterface):
    """异步版本的启动器

    用于简化和统一程序的启动操作

    """

    def __init__(self,
                 log_file_path=None, log_level=r'INFO',
                 log_file_rotation=DEFAULT_LOG_FILE_ROTATOR, log_file_retention=0xff,
                 subprocess=1, daemon=_DEFAULT_DAEMON, debug=False
                 ):

        self._process_id = 0

        if log_file_path:

            _log_file_path = Utils.path.join(
                log_file_path,
                r'runtime_{time}.log'
            )

            Utils.log.add(
                _log_file_path,
                level=log_level,
                enqueue=True,
                backtrace=debug,
                rotation=log_file_rotation,
                retention=log_file_retention
            )

        else:

            Utils.log.level(log_level)

        environment = Utils.environment()

        Utils.log.info(
            f'{hagworm_slogan}'
            f'hagworm {hagworm_version}\n'
            f'python {environment["python"]}\n'
            f'system {" ".join(environment["system"])}'
        )

        install_uvloop()

        if subprocess > 1:
            self._process_id = fork_processes(subprocess, daemon)

        self._event_loop = asyncio.get_event_loop()
        self._event_loop.set_debug(debug)

    def run(self, func, *args, **kwargs):

        Utils.log.success(f'Start process no.{self._process_id}')

        self._event_loop.run_until_complete(func(self._process_id, *args, **kwargs))

        Utils.log.success(f'Stop process no.{self._process_id}')
