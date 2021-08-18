import asyncio
from typing import Any, Dict, List

from native_rpc.exceptions import ObjectNotFoundException


class ObjectPoolEntry:
    def __init__(self, obj):
        self._obj = obj
        self._mutex = asyncio.Lock()

    @property
    def obj(self) -> Any:
        return self._obj

    @property
    def mutex(self) -> asyncio.Lock:
        return self._mutex

    async def __aenter__(self) -> Any:
        await self._mutex.acquire()
        return self._obj

    async def __aexit__(self, exc_type, exc, tb) -> None:
        self._mutex.release()


class ObjectPool:
    def __init__(self):
        self._pool: Dict[int, ObjectPoolEntry] = {}
        self._index: int = 0
        self._free_indices: List[int] = []

        self._pool_mutex = asyncio.Lock()
        self._index_mutex = asyncio.Lock()
        self._free_indices_mutex = asyncio.Lock()

    async def _alloc_index(self) -> int:
        async with self._free_indices_mutex:
            if len(self._free_indices) > 0:
                return self._free_indices.pop()

        async with self._index_mutex:
            idx = self._index
            self._index += 1
            return idx

    async def append(self, obj: Any) -> int:
        idx = await self._alloc_index()
        async with self._pool_mutex:
            self._pool[idx] = ObjectPoolEntry(obj)
            return idx

    async def pop(self, idx: Any) -> ObjectPoolEntry:
        async with self._pool_mutex:
            try:
                obj = self._pool.pop(idx)
            except KeyError:
                raise ObjectNotFoundException(idx)

        async with self._free_indices_mutex:
            self._free_indices.append(idx)

        return obj

    async def get(self, idx: int) -> ObjectPoolEntry:
        async with self._pool_mutex:
            obj = self._pool.get(idx)
            if obj is None:
                raise ObjectNotFoundException(idx)
            return obj
