import threading

from .helpers import debug_print

class Lock:
    def __init__(self, lock_type):
        self.type = lock_type
        self.lock = threading.RLock()

    def __enter__(self, *args, **kwargs):
        self.acquire(*args, **kwargs)

    def __exit__(self, type, value, traceback, *args, **kwargs):
        self.release(*args, **kwargs)

    def acquire(self, *args, **kwargs):
        #debug_print("acquiring lock for {}".format(self.type))
        self.lock.acquire(*args, **kwargs)

    def release(self, *args, **kwargs):
        #debug_print("releasing lock for {}".format(self.type))
        self.lock.release(*args, **kwargs)

