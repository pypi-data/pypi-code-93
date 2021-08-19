from asyncio import QueueEmpty, Queue
from typing import Dict


queues: Dict[int, Queue] = {}
que = {}
group_call_que = {}


async def put(chat_id: int, **kwargs) -> int:
    if chat_id not in queues:
        queues[chat_id] = Queue()
    await queues[chat_id].put({**kwargs})
    return queues[chat_id].qsize()


def get(chat_id: int) -> Dict[str, str]:
    if chat_id in queues:
        try:
            return queues[chat_id].get_nowait()
        except QueueEmpty as QeX:
            print(QeX)


def is_empty(chat_id: int) -> bool:
    if chat_id in queues:
        return queues[chat_id].empty()
    return True


def task_done(chat_id: int):
    if chat_id in queues:
        try:
            queues[chat_id].task_done()
        except ValueError:
            pass
