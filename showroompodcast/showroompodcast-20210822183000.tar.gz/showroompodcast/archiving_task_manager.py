"""Archiving task manager."""
import asyncio
from multiprocessing import Manager
from threading import Lock
from typing import Dict, List

from showroompodcast.showroom_poller import ShowroomPoller


class ArchivingTaskManager:
    """Archiving task manager."""

    def __init__(self, list_room_id: List[int]):
        # To prevent "Lock objects should only be shared between processes through inheritance"
        # see: https://stackoverflow.com/questions/25557686/python-sharing-a-lock-between-processes/25558333#25558333
        self.manager = Manager()
        self.dictionary_lock_archiving_task: Dict[int, Lock] = {
            # Reason: pylint's bug: https://github.com/PyCQA/pylint/issues/3313 pylint: disable=no-member
            room_id: self.manager.Lock()
            for room_id in list_room_id
        }

    async def poll_all_rooms(self, showroom_poller: ShowroomPoller):
        for room_id, lock_archive_task in self.dictionary_lock_archiving_task.items():
            showroom_poller.poll(room_id, lock_archive_task)
            await asyncio.sleep(1)
