# ****************       BEGIN-STANDARD-COPYRIGHT      ***************
#
# Copyright (c) 2017, Spirent Communications.
#
# All rights reserved. Proprietary and confidential information of Spirent Communications.
#
#  ***************        END-STANDARD-COPYRIGHT       ***************

import warnings
from zipfile import ZipFile, ZIP_STORED


class _QueueItem(object):
    def __init__(self, value, queue):
        self.value = value
        self.prev = None
        self.next = None
        self._queue = queue

    @property
    def queue(self):
        return self._queue

    def __repr__(self):
        return repr(self.value)


class _Queue(object):
    def __init__(self):
        self._first = None
        self._last = None
        self._size = 0

    @staticmethod
    def _attach(first, second):
        if first is not None:
            first.next = second
        if second is not None:
            second.prev = first

    def _detach(self, item):
        if item.prev is not None:
            item.prev.next = item.next
        if item.next is not None:
            item.next.prev = item.prev
        if self._first == item:
            self._first = item.next
        if self._last == item:
            self._last = item.prev
        item.next = None
        item.prev = None
        return item

    def push_last(self, value):
        item = _QueueItem(value, self)
        self._attach(self._last, item)
        self._last = item
        self._first = self._first or item
        self._size += 1
        return item

    def pop_first(self):
        if not self:
            raise IndexError('pop_first from empty queue')
        self._size -= 1
        return self._detach(self._first).value

    def shift_last(self, item):
        if item.queue is not self:
            raise ValueError('shift foreign item')
        self._detach(item)
        self._attach(self._last, item)
        self._last = item
        self._first = self._first or item

    def remove(self, item):
        if item.queue is not self:
            raise ValueError('removing foreign item')
        self._detach(item)
        self.size -= 1
        return item

    def __len__(self):
        return self._size


class LRUCache(object):
    def __init__(self, storage, max_size):
        self._storage = storage
        self._max_size = max_size
        self._queue = _Queue()
        self._index = {}
        self._total_item_size = 0

    def __contains__(self, key):
        return key in self._index

    def __getitem__(self, key):
        if key in self._index:
            item = self._index[key]
            self._queue.shift_last(item)
            key, value, size = item.value
            return value

        value, size = self._retrieve(key)

        self._index[key] = self._queue.push_last((key, value, size))
        self._total_item_size += size
        self._clear()
        return value

    def __delitem__(self, key):
        if key in self._index:
            item = self._index[key]
            self._queue.remove(item)
            del self._index[key]
            key, value, size = item.value
            self._total_item_size -= size

    def _retrieve(self, key):
        try:
            return self._storage[key]
        except KeyError:
            raise KeyError(key)

    def _clear(self):
        while self._total_item_size > self._max_size and len(self._index) > 1:
            key, value, size = self._queue.pop_first()
            del self._index[key]
            self._total_item_size -= size

    def __repr__(self):
        return repr(self._index)

    @property
    def size(self):
        return self._total_item_size

    def keys(self):
        return self._index.keys()


class ZipFileStorage(object):
    def __init__(self, stream, deserialize=lambda x: x, serialize=str):
        self._file = stream
        self._zipfile = ZipFile(self._file, mode='a', compression=ZIP_STORED)
        self._deserialize = deserialize
        self._serialize = serialize

    def __del__(self):
        self.close()

    def close(self):
        self._zipfile.close()

    def load(self, entry_name):
        entry = self._zipfile.getinfo(entry_name)
        data = self._zipfile.read(entry)
        size = len(data)
        value = self._deserialize(data)
        return value, size

    def __getitem__(self, key):
        return self.load(key)

    def store(self, entry_name, value):
        data = self._serialize(value)
        with warnings.catch_warnings():
            # we will overwrite some steps and get warning of entry key already in use
            warnings.simplefilter("ignore")
            self._zipfile.writestr(entry_name, data)
        return len(data)

    def __repr__(self):
        return repr(self._zipfile.namelist())
