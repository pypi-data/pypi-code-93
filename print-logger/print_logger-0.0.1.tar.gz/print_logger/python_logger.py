import os
import threading
import inspect
from datetime import datetime

INFO = 'INFO'
WARNING = 'WARNING'
ERROR = 'ERROR'

def print_log(level, message):
    now = datetime.now()
    pid = os.getpid()
    current_thread = threading.current_thread()
    thread_id = f'{current_thread.getName()}-{current_thread.native_id}-{current_thread.ident}'

    # temporarily empty
    trace_id = ''

    callerframerecord = inspect.stack()[1]
    frame = callerframerecord[0]
    info = inspect.getframeinfo(frame)

    log_str = f'{now}|{trace_id}|{pid}|{thread_id}|{level}|{info.filename}-{info.lineno}|{str(message)}'
    print(log_str)
