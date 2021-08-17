import pathlib
import concurrent.futures
import threading
import time
import sys


"""
LOCK SAUCE:
    GLOBAL LOCK:
    'e' - exited
    '1' - high state
    '' - low state

    MAX LOCK:
        '1' - someone tried to open
        'e' - close application [TODO]

    Rash is opened if it toggle s between high and low state for every second

"""


class Launcher:
    def __init__(self, pwd, manager: concurrent.futures.ThreadPoolExecutor):
        self.pwd = pathlib.Path(pwd)
        self.pwd = self.pwd.parent if self.pwd.is_file() else self.pwd

        if not self.pwd.exists():
            raise FileNotFoundError(self.pwd)

        self.global_mutex = self.pwd / "GLOBAL.lock"
        self.max_mutex = self.pwd / "MAX.lock"

        None if self.test() else self._notify()

        self.workers = threading.Lock(), threading.Lock()

        manager.submit(
            self.read_thread
        )

        manager.submit(
            self.write_thread
        )

        self.remainder = None

    def _notify(self):
        self.max_mutex.write_text("1")
        return sys.exit(0)

    def register(self):
        pass

    def test(self):
        if not self.global_mutex.exists():
            self.global_mutex.write_text("")
            return True

        test_1 = self.global_mutex.read_text()

        if test_1 == 'e':
            return True

        time.sleep(1)

        test_2 = self.global_mutex.read_text()

        time.sleep(0.1)

        test_3 = self.global_mutex.read_text()

        if test_1 == test_2 and test_3 == test_1:
            return True

        return False

    def read_thread(self):
        self.workers[0].acquire()

        while self.workers[0].locked():

            code = None if self.max_mutex.exists() else self.max_mutex.write_text("")
            code = code if code else self.max_mutex.read_text()

            result = None if code == '' else self.remainder(code == '1') if self.remainder else None

            if result:
                break

            time.sleep(1)

        self.max_mutex.write_text("")

    def write_thread(self):
        self.workers[1].acquire()

        toggle = False

        while self.workers[1].locked():
            None if self.global_mutex.exists() else self.global_mutex.write_text("")

            self.global_mutex.write_text("" if toggle else "1")
            toggle = not toggle

            time.sleep(1)

    def close(self):
        for _ in self.workers:
            _.release()
