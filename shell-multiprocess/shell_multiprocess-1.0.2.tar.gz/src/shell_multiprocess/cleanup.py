import sys
import asyncio
import psutil
import concurrent.futures
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .async_processor import AsyncProcessor


class CleanupAsyncProcessor:
    """Cleanup class for AsyncProcessor if there would be any processes
    which would be troublesome to kill. Currently the KeyInterruptError
    cancels and kills all shell processes but that might be too optimistic
    when a process is KeyInterruptError-proof and requires a forced cleanup.

    The event loop cannot be stopped before running cleanup.

    Example usage:

    loop = asyncio.get_event_loop()
    processor = AsyncProcessor(2)
    try:
        loop.run_until_complete(processor.start(cmds))
    except KeyboardInterrupt:
        processor.stop()
        cleanup = CleanupAsyncProcessor(processor, loop)
        loop.run_until_complete(cleanup.start())
    finally:
        loop.close()
        exit(processor.returncode)
    """

    def __init__(
        self,
        processor: "AsyncProcessor",
        loop: asyncio.AbstractEventLoop,
        kill_signal: int,
    ):
        self.processor = processor
        if not self.processor.stopped:
            print("Processor was not stopped. Force stopping", file=sys.stderr)
            self.processor.stop()
        self.loop = loop
        self.kill_signal = kill_signal

    async def start(self):
        self._cancel_pending()
        await self._cleanup_commands()
        await self._cleanup_shells()
        await self._cleanup_logger()

    async def _cleanup_logger(self):
        self.processor.filelogger.set_running_to_interrupted()
        self.processor.filelogger.set_waiting_to_never_ran()
        await self.processor.filelogger.update_logfile()

    def _get_executor(self):
        return concurrent.futures.ThreadPoolExecutor(
            max_workers=self.processor.process_count
        )

    def _cancel_pending(self):
        for future in self.processor.pending:
            future.cancel()

    async def _cleanup_commands(self):
        child_proc_tasks = set()
        executor = self._get_executor()
        for process_obj in self.processor.process_pool:
            task = self.loop.run_in_executor(
                executor,
                self._kill_child_processes,
                process_obj.pid,
                self.kill_signal,
            )
            child_proc_tasks.add(task)
        await asyncio.wait(child_proc_tasks)

    async def _cleanup_shells(self):
        for process_obj in self.processor.process_pool:
            try:
                process_obj.kill()
            except ProcessLookupError:
                pass
        finished, pending = await asyncio.wait(
            [p.wait() for p in self.processor.process_pool]
        )

    @staticmethod
    def _kill_child_processes(parent_pid: int, kill_signal: int):
        try:
            parent = psutil.Process(parent_pid)
        except psutil.NoSuchProcess:
            return
        try:
            child_processes = parent.children(recursive=False)
        except psutil.NoSuchProcess:
            pass
        else:
            for process in child_processes:
                process.send_signal(kill_signal)
