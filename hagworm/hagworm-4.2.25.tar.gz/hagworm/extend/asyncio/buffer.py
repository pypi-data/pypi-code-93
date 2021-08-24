# -*- coding: utf-8 -*-

from tempfile import TemporaryFile

from .base import Utils
from .task import IntervalTask

from hagworm.extend.base import ContextManager


class _DataBase:

    def __init__(self):

        self._data_list = []

    def append(self, data):

        self._data_list.append(data)

    def extend(self, data_list):

        self._data_list.extend(data_list)


class DataQueue(_DataBase):

    def __init__(self, maxsize=1):

        super().__init__()

        self._task_list = set()

        self._task_maxsize = maxsize

    def _create_task(self):

        if len(self._data_list) > 0:

            task = Utils.create_task(
                self._handle_data(
                    self._data_list.pop(0)
                )
            )

            task.add_done_callback(self._done_callback)

            self._task_list.add(task)

            return True

        else:

            return False

    def _done_callback(self, task):

        if task in self._task_list:
            self._task_list.remove(task)
            self.pop_data()

    async def _handle_data(self, data):
        raise NotImplementedError()

    def set_maxsize(self, val):

        self._task_maxsize = val

    def pop_data(self):

        result = 0

        while len(self._task_list) < self._task_maxsize:
            if self._create_task():
                result += 1
            else:
                break

        return result


class DataAsyncQueue(DataQueue):

    def __init__(self, maxsize=1):

        super().__init__(maxsize)

        self._task_size = 0

    def set_task_done(self, val=1):

        self._task_size -= val

        self.pop_data()

    def pop_data(self):

        result = 0

        while self._task_size < self._task_maxsize:

            if self._create_task():
                self._task_size += 1
                result += 1
            else:
                break

        return result


class QueueBuffer(_DataBase):

    def __init__(self, maxsize, timeout=0):

        super().__init__()

        self._timer = None

        self._maxsize = maxsize

        if timeout > 0:
            self._timer = IntervalTask.create(timeout, self._handle_buffer)
            self._timer.start()

    def _handle_buffer(self):

        if len(self._data_list) > 0:
            data_list, self._data_list = self._data_list, []
            Utils.call_soon(self._run, data_list)

    async def _run(self, data_list):
        raise NotImplementedError()

    def append(self, data):

        super().append(data)

        if len(self._data_list) >= self._maxsize:
            self._handle_buffer()

    def extend(self, data_list):

        super().extend(data_list)

        if len(self._data_list) >= self._maxsize:
            self._handle_buffer()


class FileBuffer(ContextManager):
    """文件缓存类
    """

    def __init__(self, slice_size=0x1000000):

        self._buffers = []

        self._slice_size = slice_size

        self._read_offset = 0

        self._append_buffer()

    def _context_release(self):

        self.close()

    def _append_buffer(self):

        self._buffers.append(TemporaryFile())

    def close(self):

        while len(self._buffers) > 0:
            self._buffers.pop(0).close()

        self._read_offset = 0

    def write(self, data):

        buffer = self._buffers[-1]

        buffer.seek(0, 2)
        buffer.write(data)

        if buffer.tell() >= self._slice_size:
            buffer.flush()
            self._append_buffer()

    def read(self, size=None):

        buffer = self._buffers[0]

        buffer.seek(self._read_offset, 0)

        result = buffer.read(size)

        if len(result) == 0 and len(self._buffers) > 1:
            self._buffers.pop(0).close()
            self._read_offset = 0
        else:
            self._read_offset = buffer.tell()

        return result
