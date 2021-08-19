import asyncio
from typing import Tuple
import subprocess


async def run_async(cmd: str) -> Tuple[int, bytes, bytes]:
    prc = await asyncio.create_subprocess_shell(
        cmd,
        stdin=None,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await prc.communicate()
    return prc.returncode, stdout, stderr


def run_sync(cmd: str) -> Tuple[int, bytes, bytes]:
    prc = subprocess.run(
        cmd,
        stdin=None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True
    )
    return prc.returncode, prc.stdout, prc.stderr
