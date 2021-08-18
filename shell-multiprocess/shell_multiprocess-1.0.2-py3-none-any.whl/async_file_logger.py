import asyncio
import time, os, sys
from functools import partial
from dataclasses import dataclass, field
from datetime import datetime as dt, timedelta as td
from enum import Enum
from typing import List, Optional
from pathlib import Path
import os
from functools import wraps
import aiofiles


class Status(Enum):
    Waiting = "waiting"
    Error = "error"
    Done = "done"
    Running = "running"
    Interrupted = "interrupted"
    NeverRan = "never-ran"


@dataclass
class LogLine:
    cmd: str
    status: Status = field(default=Status.Waiting)
    start: dt = field(default=None, repr=False)
    end: dt = field(default=None, repr=False)

    def set_start(self):
        self.start = dt.now()

    def set_end(self):
        self.end = dt.now()

    @property
    def elapsed(self) -> Optional[td]:
        if self.start and self.end:
            return self.end - self.start


class AsyncFileLogger:
    _template = (
        "{status:11.11} | {start:^19.19} | {end:^19.19} | {elapsed:^19.19} | {cmd}\n"
    )

    def __init__(
        self,
        cmds: List[str],
        filename=f"multiprocess_{os.getpid()}.log",
        disable_logging=False,
    ):
        self._loglines = [LogLine(label) for label in cmds]
        self.indexed_cmds = list(enumerate(cmds))
        self._filename = filename
        if os.path.exists(self._filename):
            print(f"File already exists: '{filename}'", file=sys.stderr)
        self.disabled = disable_logging

    def set_running_to_interrupted(self):
        for logline in self._loglines:
            if logline.status is Status.Running:
                logline.status = Status.Interrupted

    def set_waiting_to_never_ran(self):
        for logline in self._loglines:
            if logline.status is Status.Waiting:
                logline.status = Status.NeverRan

    async def set_running_and_update(self, index):
        log_line = self._loglines[index]
        log_line.set_start()
        log_line.status = Status.Running
        await self.update_logfile()

    async def set_done_and_update(self, index):
        log_line = self._loglines[index]
        log_line.set_end()
        log_line.status = Status.Done
        await self.update_logfile()

    async def set_error_and_update(self, index):
        log_line = self._loglines[index]
        log_line.set_end()
        log_line.status = Status.Error
        await self.update_logfile()

    async def update_logfile(self):
        if self.disabled:
            return
        async with aiofiles.open(self._filename, "w") as f:
            await f.write(self.get_log_str())

    def get_log_str(self):
        out = self._get_header() + "".join(self._get_formatted_loglines())
        return out

    def _get_header(self):
        breakline = 100 * "-"
        line1 = self._template.format(
            status="status", start="start", end="end", elapsed="elapsed", cmd="command"
        )
        line2 = self._template.format(
            status=breakline,
            start=breakline,
            end=breakline,
            elapsed=breakline,
            cmd="-------",
        )
        return line1 + line2

    def _get_formatted_loglines(self):
        return [self._format_logline(line) for line in self._loglines]

    def _format_logline(self, logline: LogLine):
        start = self._format_datetime(logline.start)
        end = self._format_datetime(logline.end)
        elapsed = self._format_timedelta(logline.elapsed)
        status = logline.status.value
        return self._template.format(
            status=status, start=start, end=end, elapsed=elapsed, cmd=logline.cmd
        )

    @staticmethod
    def _format_datetime(date_time: dt):
        return str(date_time).split(".")[0] if date_time is not None else "N/A"

    @staticmethod
    def _format_timedelta(time_delta: td):
        return str(time_delta) if time_delta is not None else "N/A"


if __name__ == "__main__":
    logger = AsyncFileLogger(["true", "false"], disable_logging=True)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(logger.set_running_and_update(0))
    print(logger.get_log_str())

    # logger.finish(0)
    # logger.error(1)
