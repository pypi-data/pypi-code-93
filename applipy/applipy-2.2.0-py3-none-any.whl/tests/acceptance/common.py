import sys
import os
import time
from typing import Any, Literal
from subprocess import Popen


class ApplipyProcess:

    def __init__(self, config_path: str, applipy_env: str, env: dict[str, str] = {}) -> None:
        self._env = os.environ.copy()
        self._env['APPLIPY_CONFIG_PATH'] = config_path
        self._env['APPLIPY_ENV'] = applipy_env
        self._env.update(env)

    def __enter__(self) -> Popen[bytes]:
        self._process = Popen(('python', '-m', 'applipy'), stdout=sys.stdout, stderr=sys.stderr, env=self._env)
        time.sleep(1)
        return self._process

    def __exit__(self, *args: Any) -> Literal[False]:
        self._process.terminate()
        self._process.wait()
        return False
