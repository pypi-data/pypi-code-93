import asyncio
import threading
from typing import Union, Iterable, Coroutine


class Thread(threading.Thread):
    def __init__(self, func: Union[asyncio.Queue, Iterable, Coroutine], workers: int = 1) -> None:
        super().__init__()
        self.workers = workers
        self.running = False

        self.queue = func if isinstance(func, asyncio.Queue) else asyncio.Queue()

        if self.queue.empty():
            if isinstance(func, Iterable):
                for i in func:
                    self.queue.put_nowait(i)
            else:
                self.workers = 1
                self.queue.put_nowait(func)

    async def _worker(self) -> None:
        while self.running:
            try:
                await self.queue.get_nowait()
            except asyncio.QueueEmpty:
                return

    def stop(self) -> None:
        self.running = False

    def run(self) -> None:
        asyncio.set_event_loop(asyncio.SelectorEventLoop())

        self.running = True

        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.gather(*[self._worker() for _ in range(self.workers)]))
        loop.close()
