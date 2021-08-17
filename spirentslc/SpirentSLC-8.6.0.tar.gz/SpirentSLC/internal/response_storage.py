# ****************       BEGIN-STANDARD-COPYRIGHT      ***************
#
# Copyright (c) 2017, Spirent Communications.
#
# All rights reserved. Proprietary and confidential information of Spirent Communications.
#
#  ***************        END-STANDARD-COPYRIGHT       ***************

from os import remove, close, path
from platform import system
from tempfile import TemporaryFile, mkstemp

from . import ExecutionProtocol_pb2 as pb
from .cache import LRUCache, ZipFileStorage
from ..session_response import SessionActionResponse


def serialize(response):
    return response.message.SerializeToString()


def deserialize(data):
    response_message = pb.SessionActionResponse()
    response_message.ParseFromString(data)
    return SessionActionResponse(response_message)


class ResponseStorage(object):
    def __init__(self, max_size=10 * 1024 * 1024):
        # Windows can't work with a TemporaryFile consistently
        self._create_temp_file()
        self._storage = ZipFileStorage(self._temp_file, serialize=serialize, deserialize=deserialize)
        self._cache = LRUCache(self._storage, max_size)
        self._ids = set()

    def __del__(self):
        self.close()

    def _create_temp_file(self):
        if system() == "Windows":
            (self._fd, self._temp_file) = mkstemp(suffix="Slc")
        else:
            self._temp_file = TemporaryFile()

    def close(self):
        self._storage.close()
        if system() == "Windows":
            if path.isfile(self._temp_file):
                close(self._fd)
                remove(self._temp_file)

    def __getitem__(self, step_id):
        if step_id not in self._ids:
            raise KeyError(step_id)
        return self._cache[step_id]

    def __setitem__(self, step_id, response):
        self._storage.store(step_id, response)
        del self._cache[step_id]  # invalidate cache entry
        self._ids.add(step_id)

    def __contains__(self, step_id):
        return step_id in self._ids

    def __len__(self):
        return len(self._ids)

    def keys(self):
        return iter(self._ids)
