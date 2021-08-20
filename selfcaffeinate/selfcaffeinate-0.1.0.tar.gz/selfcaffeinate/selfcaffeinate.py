import os
from subprocess import Popen


class SelfCaffeinate:

    CAFFEINATE_PATH = "/usr/bin/caffeinate"

    def __init__(self, caffeinate_path=CAFFEINATE_PATH):
        pid = os.getpid()
        pid = str(pid)
        caffeinate_argv = [caffeinate_path, "-w", pid]
        self._p = Popen(caffeinate_argv)

    def __del__(self):
        self._p.terminate()

    def __enter__(self):
        pass

    def __exit__(self):
        pass
