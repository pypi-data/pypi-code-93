#               Copyright (c) 2021 Zenqi.

# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


import asyncio
import os
import signal
import inspect
from typing import Any, Dict, Tuple
from typing import Callable
from typing import Optional
from typing import Type
from typing import cast
from typing import List

from .watcher import FileWatcher
from .utils import get_root_path
from .event import Event
from .event import EventType

from multiprocessing import Process


class Rload:
    """
    A hot code reloader for modern Python 3.
    With Event Handling and more.

    Parameters:
    ---
        name(str):
            The name of the module. Just pass `__name__`

        ignored_paths(List[str]):
            The list of paths to be ignore

        watcher_cls(FileWatcher):
            A class of FileWatcher. It can be `PythonWatcher` or more

    """

    __event = Event()
    __event_triggered = False

    def __init__(
        self,
        name: str,
        ignored_paths: Optional[List[str]] = [],
        *,
        delay: Optional[float] = 0,
        watcher_cls: Type["FileWatcher"] = FileWatcher,
        loop: Optional[asyncio.AbstractEventLoop] = None
    ):

        self.name = name
        self.root = get_root_path(self.name)
        self.loop = loop or asyncio.get_event_loop()

        self.delay = delay
        self.ignored_paths = ignored_paths
        self.watcher_cls = watcher_cls(self.root, self.ignored_paths)

    def on(self, type, handler: Callable[..., Any] = None):
        """
        A wrapper for `event.Event.on()`
        """
        return self.__event.on(type, handler)

    async def _watch_loop(self):
        """
        A coroutine function for watching files on a loop.
        This function cannot be implemented on non-async func.
        use `Rload.watch()` instead.

        """

        self.watcher_cls.watch()

        if self.watcher_cls.added:
            self.__event_triggered = True
            self.__event.emit("change", EventType.ADDED, self.watcher_cls.changes)
            self.watcher_cls.added = []

        elif self.watcher_cls.removed:
            self.__event_triggered = True
            self.__event.emit("change", EventType.REMOVED, self.watcher_cls.changes)
            self.watcher_cls.removed = []

        elif self.watcher_cls.modified:
            self.__event_triggered = True
            self.__event.emit("change", EventType.MODIFIED, self.watcher_cls.changes)
            self.watcher_cls.modified = []

        await asyncio.sleep(delay=self.delay)

    def watch(self):
        """
        Run the Rload class. You can use the `__call__`
        method as well.

        Example:
        ---
            >>> rload = Rload(__name__)
            >>> rload.on('change')
            >>> def handle_change(type, data):
            >>>   ...
            >>>   ...
            >>> if __name__ == '__main__':
            >>>   rload.watch()

        """

        self.__create_loop([self._watch_loop])

    def run(self, target: Callable[..., Any] = None, *args, **kwargs):
        """
        Reload the command
        """

        process = self._start_process(target=target, args=args, kwargs=kwargs)
        process_path = os.path.abspath(inspect.getfile(target))

        async def reloader():
            if self.__event_triggered:

                self.__event.emit("reload", process_path)
                self._stop_process(process)
                self._start_process(target=target, args=args, kwargs=kwargs)
                self.__event.emit("reloaded", process_path)
                self.__event_triggered = False

        self.__create_loop([self._watch_loop, reloader])

    def _start_process(
        self,
        target: Callable[..., Any],
        args: Tuple[Any, ...],
        kwargs: Optional[Dict[str, Any]],
    ):
        """
        Strt the given process.

        Parameters:
        ---
            target (Function):
                The function to be added

            *args (Tuple):
                The args of the function if there is

            **kwargs (Dict):
                The kwargs of the function if there is

        """

        process = Process(target=target, args=args, kwargs=kwargs)
        process.start()
        return process

    def _stop_process(self, process: Process):
        """
        Stop the process if the process is running.

        Parameters:
        ---
            process (multiprocessing.Process):
                The process to be stopped.

        """
        if process.is_alive():
            pid = cast(int, process.pid)
            os.kill(pid, signal.SIGINT)
            process.join(5)
            if process.exitcode is None:

                os.kill(pid, signal.SIGKILL)
                process.join(1)
            else:
                # NOTE: Process stopped.
                pass
        else:
            # NOTE: Process already dead
            pass

    def __create_loop(self, functions: List[Callable[..., Any]] = None):
        """
        Create a loop within the function given. The list of function
        must be coroutine.

        Parameters:
        ---
            functions (List):
                List of coroutine functions.

        """

        loop = self.loop

        try:
            loop.add_signal_handler(signal.SIGINT, lambda: loop.stop())
            loop.add_signal_handler(signal.SIGTERM, lambda: loop.stop())
        except Exception:
            pass

        async def run_loop():

            while True:
                for handler in functions:
                    await handler()

        def stop_loop_on_completion(f):
            loop.stop()

        future = asyncio.ensure_future(run_loop(), loop=loop)
        future.add_done_callback(stop_loop_on_completion)

        try:
            loop.run_forever()
        except KeyboardInterrupt:
            loop.stop()
        finally:
            future.remove_done_callback(stop_loop_on_completion)

    def __call__(self):
        """
        A wrapper for `Rload.run()`.

        Example:
        ---
            >>> rload = Rload(__name__)
            >>> rload.on('change')
            >>> def handle_change(type, data):
            >>>   ...
            >>>   ...
            >>> if __name__ == '__main__':
            >>>   rload()

        """
        return self.run()
