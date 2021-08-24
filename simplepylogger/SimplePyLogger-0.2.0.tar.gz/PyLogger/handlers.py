import os
import sys
import glob
import threading
import weakref
import itertools

try:
    from constants import LoggerLevels
except ImportError:
    from .constants import LoggerLevels

_handlers_ref = weakref.WeakValueDictionary()
_handlers = []
_lock = threading.RLock()


def register_handler(handler):
    _lock.acquire()
    try:
        _handlers.append(weakref.ref(handler, remove_handler))
    finally:
        _lock.release()


def remove_handler(handler):
    _lock.acquire()
    try:
        _handlers.remove(handler)
    finally:
        _lock.release()


class Handler:

    def __init__(self):
        self._name = None
        self._closed = False
        self._lock = threading.RLock()

        register_handler(self)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        if not name:
            return

        _lock.acquire()
        try:
            if self._name in _handlers_ref:
                _handlers_ref[name] = _handlers_ref.pop(self._name)
                self._name = name
                return

            _handlers_ref[name] = self
            self._name = name

        finally:
            _lock.release()

    def remove(self):
        _lock.acquire()
        try:
            self._closed = True
            if self._name and self._name in _handlers_ref:
                del _handlers_ref[self._name]
        finally:
            _lock.release()

    def emit(self, msg):
        raise NotImplementedError("Must be implemented in subclass.")

    def flush(self):
        raise NotImplementedError("Must be implemented in subclass.")

    def handle(self, msg, level, color=True):

        self._lock.acquire()

        try:
            if color and level > LoggerLevels.info:
                self.emit(LoggerLevels.level_color[level] + msg + LoggerLevels.level_color['end'])
            else:
                self.emit(msg)
        finally:
            self._lock.release()


class StreamHandler(Handler):
    def __init__(self, stream=None):

        super().__init__()

        if stream is None:
            stream = sys.stdout
            self.name = f'{os.path.basename(stream.name)}'
        else:
            self.name = f'<{os.path.basename(stream.name)}>'

        self.stream = stream

    def flush(self):
        self._lock.acquire()
        try:
            if self.stream and hasattr(self.stream, "flush"):
                self.stream.flush()
        finally:
            self._lock.release()

    def emit(self, msg):
        try:
            self.stream.write(msg + '\n')
            self.flush()
        except Exception:
            raise

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.name}>'


class FileHandler(StreamHandler):
    def __init__(self, filename, mode='a', encoding=None):
        self.filename = os.fspath(filename)
        self.full_path = os.path.abspath(filename)
        self.mode = mode
        self.encoding = encoding

        super().__init__(self.open())

    def open(self):
        return open(self.full_path, self.mode, encoding=self.encoding)

    def close(self):
        try:
            try:
                self.stream.flush()
            finally:
                stream = self.stream
                self.stream = None
                stream.close()
        finally:
            StreamHandler.remove(self)

    def emit(self, msg):
        if self.stream is None:
            if self.mode != 'w' or not self._closed:
                self.stream = self.open()
        if self.stream:
            StreamHandler.emit(self, msg)

    def handle(self, msg, level):
        Handler.handle(self, msg, level, color=False)

        self.close()


class RotatingFileHandler(FileHandler):
    def __init__(self, filename, backup_count, mode='a', encoding=None):
        self.filename = os.fspath(filename)
        self.backup_count = backup_count
        self.mode = mode
        self.encoding = encoding

        log_files_to_delete = itertools.islice(self._get_log_files(), self.backup_count, None)

        for file in list(log_files_to_delete):
            os.remove(file)

        super().__init__(self.filename, mode=self.mode, encoding=self.encoding)

    def _get_log_files(self):
        log_dir = os.path.dirname(os.path.abspath(self.filename))
        log_files = glob.glob(log_dir + '/*.log')
        log_files.sort(key=lambda f: os.stat(f).st_mtime, reverse=True)
        return iter(log_files)


if __name__ == '__main__':
    text = input('text: ')
    fh = RotatingFileHandler('./.logs/test1.log', backup_count=5)

    fh.handle(text, level=0)
    fh = RotatingFileHandler('./.logs/test2.log', backup_count=5)
    fh.handle(text, level=0)
