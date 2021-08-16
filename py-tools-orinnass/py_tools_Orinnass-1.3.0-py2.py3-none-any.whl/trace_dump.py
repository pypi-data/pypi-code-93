import tracemalloc
from threading import Thread
from tracemalloc import StatisticDiff, Statistic
from typing import Union, List, Optional
from datetime import datetime
from time import sleep
from os import getenv


_trace_dump_enabled = False
_last_dump = None


def _print_trace_dump(dump: Union[List[StatisticDiff], List[Statistic]], file: str, start_message: str):
    with open(file, 'a') as file_dump:
        dump_message = f'{datetime.now()}   {start_message}\n'
        for i, stat in enumerate(sorted(dump, key=lambda value: value.size, reverse=True)[:6], 1):
            dump_message += f'{i}  {str(stat)}\n'
        file_dump.write(dump_message)


def _create_snapshot(dump_file: str, start_message: str = "start dump", print_snapshot_in_file: bool = True):
    global _last_dump

    current_snapshot = tracemalloc.take_snapshot()
    if _last_dump:
        stats = current_snapshot.compare_to(_last_dump, 'filename')
    else:
        stats = current_snapshot.statistics('filename')
    _last_dump = current_snapshot

    if print_snapshot_in_file:
        _print_trace_dump(stats, dump_file, start_message=start_message)


def _cron_trace_dump(dump_file: str, sleep_time: Optional[int]):
    global _trace_dump_enabled
    global _last_dump
    _trace_dump_enabled = True

    if sleep_time and sleep_time != 'None':
        sleep_time = int(sleep_time)
        while _trace_dump_enabled:
            sleep(sleep_time)
            _create_snapshot(dump_file, start_message="compare snapshot")


def create_snapshot(snapshot_message: str):
    _create_snapshot(getenv('FILE_DUMP'), start_message=snapshot_message)


def start_trace_dump():
    if getenv('TRACE_DUMP'):
        if not getenv("FILE_DUMP"):
            raise KeyError('Не задана переменная FILE_DUMP', {'variable': "FILE_DUMP"})
        if not getenv('INTERVAL_DUMP'):
            raise KeyError('Не задана переменная INTERVAL_DUMP', {'variable': "INTERVAL_DUMP"})

        trace_dump_thread = Thread(target=_cron_trace_dump, name="cron_trace_dump", daemon=True,
                                   args=(getenv('FILE_DUMP'), getenv('INTERVAL_DUMP')))

        tracemalloc.start()
        _create_snapshot(getenv('FILE_DUMP'))
        trace_dump_thread.start()


def stop_trace_dump():
    global _trace_dump_enabled
    _trace_dump_enabled = False
    tracemalloc.stop()
