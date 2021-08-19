import os

from .utils.cmd import run_async, run_sync
from .utils.re import is_youtube_link
from .exceptions import FFmpegError, YouTubeDLError
from .controllers import AsyncController, SyncController


class AsyncConverter(AsyncController):
    async def _solve_input(self, input: str):
        if is_youtube_link(input):
            code, out, _ = await run_async(self._get_youtube_dl_cmd(input))

            if code != 0:
                raise YouTubeDLError(f"Got a non-zero return code: {code}")

            return f"\"{out.decode().strip()}\""

        return input

    async def convert(self, input: str) -> str:
        output = self._get_output(input)

        if os.path.isfile(output):
            return output

        input = await self._solve_input(input)
        code, _, _ = await run_async(self._get_ffmpeg_cmd(input, output))

        if code != 0:
            raise FFmpegError(f"Got a non-zero return code: {code}")

        return output


class SyncConverter(SyncController):
    def _solve_input(self, input: str):
        if is_youtube_link(input):
            code, out, _ = run_sync(self._get_youtube_dl_cmd(input))

            if code != 0:
                raise YouTubeDLError(f"Got a non-zero return code: {code}")

            return f"\"{out.decode().strip()}\""

        return input

    def convert(self, input: str) -> str:
        output = self._get_output(input)

        if os.path.isfile(output):
            return output

        input = self._solve_input(input)
        code, _, _ = run_sync(self._get_ffmpeg_cmd(input, output))

        if code != 0:
            raise FFmpegError(f"Got a non-zero return code: {code}")

        return output
