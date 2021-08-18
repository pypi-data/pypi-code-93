import asyncio
from collections import deque
from typing import List, Set
from .async_file_logger import AsyncFileLogger


class AsyncProcessor:
    def __init__(self, process_count: int, cmds: List[str], log_to_file: bool = False):
        self._process_count = process_count
        self.process_pool: List[asyncio.subprocess.Process] = []
        self.pending: Set[asyncio.Task] = set()
        self.stopped = False
        self.filelogger = AsyncFileLogger(cmds, disable_logging=not log_to_file)

    @property
    def process_count(self):
        return self._process_count

    def stop(self):
        self.stopped = True

    @property
    def returncode(self):
        if any(p.returncode for p in self.process_pool if p.returncode is not None):
            return 1
        if any(p.returncode is None for p in self.process_pool):
            return 2
        return 0

    async def start(self):
        indexed_cmds = self.filelogger.indexed_cmds.copy()
        pending = await self._get_pending_tasks(indexed_cmds[: self.process_count])
        self.pending.update(pending)
        remaining_cmds = deque(indexed_cmds[self.process_count :])

        while remaining_cmds and not self.stopped:
            finished, self.pending = await asyncio.wait(
                self.pending, return_when=asyncio.FIRST_COMPLETED
            )
            if self.stopped:
                return

            new_cmds = self._pop_cmds(remaining_cmds, len(finished))
            new_tasks = await self._get_pending_tasks(new_cmds)
            self.pending.update(new_tasks)

        for f in asyncio.as_completed(self.pending):
            await f
            if self.stopped:
                return

    @staticmethod
    def _pop_cmds(cmds: deque, no_elements_to_pop: int):
        poped_cmds = []
        for _ in range(no_elements_to_pop):
            try:
                cmd = cmds.popleft()
            except IndexError:
                break
            else:
                poped_cmds.append(cmd)
        return poped_cmds

    async def _get_pending_tasks(self, indexed_cmds):
        coros = {self._get_command_coro(idx, cmd) for idx, cmd in indexed_cmds}
        tasks = {asyncio.ensure_future(coro) for coro in coros}
        return tasks

    async def _get_command_coro(self, index, cmd):
        process_obj = await asyncio.subprocess.create_subprocess_shell(cmd)
        self.process_pool.append(process_obj)
        await self.filelogger.set_running_and_update(index)
        await process_obj.wait()
        if process_obj.returncode == 0:
            await self.filelogger.set_done_and_update(index)
        else:
            await self.filelogger.set_error_and_update(index)


#
#
# cmds = [
#     "sleep 1; date && echo 4a",
#     "sleep 1; date && echo 4b",
#     "sleep 1; date && echo 31c",
#     "sleep 1; date && echo 3false && false",
#     "sleep 100; date && echo 3b",
#     "sleep 100; date && echo 3c",
#     "sleep 100; date && echo 3d",
# ]
