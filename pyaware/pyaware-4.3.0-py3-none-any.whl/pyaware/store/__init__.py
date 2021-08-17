from pyaware.store.memory import MemoryStore
from pyaware.store.disk import DiskStorage
import typing


memory_storage = MemoryStore()
disk_storage: typing.Optional[DiskStorage] = None
