# -*- coding: utf-8 -*-
import logging
import queue
import traceback

from threading import Thread
from .dlso import dict2obj

class ConcurrencyException(Exception):
    pass

class Worker(Thread):
    """
    Thread executing tasks from a given tasks queue.
    """
    def __init__(self, tasks, timeout_seconds):
        Thread.__init__(self)
        self.tasks = tasks
        self.timeout = timeout_seconds
        self.daemon = True
        self.start()

    def run(self):
        while True:
            try:
                func, args, kargs = self.tasks.get(timeout=self.timeout)
            except queue.Empty:
                # Extra thread allocated, no job, exit gracefully
                break
            try:
                func(*args, **kargs)
            except Exception:
                traceback.print_exc()
            self.tasks.task_done()

class ThreadPool:
    def __init__(self, num_threads, timeout_seconds):
        self.tasks = queue.Queue(num_threads)
        for _ in range(num_threads):
            Worker(self.tasks, timeout_seconds)

    def add_task(self, func, *args, **kargs):
        self.tasks.put((func, args, kargs))

    def wait_completion(self):
        self.tasks.join()

class MTask(object):
    def __init__(self, cbfunc, **kwarg):
        self.cbfunc = cbfunc
        self.kwarg = kwarg
        self.result = None

    def send(self):
        try:
            self.result = self.cbfunc(**self.kwarg)
        except Exception:
            logging.error(traceback.format_exc())

def multithread_task(cbfunc, args, settings=None):
    """Execute multiple task via mthreading, order of tasks is stable
    returns same tasks but with return variables filled.
    
    thread_num: default is 5
    thread_timeout: in seconds
    """
    settings = dict2obj(settings) if isinstance(settings, dict) else settings
    num_threads = getattr(settings, 'thread_num', 5)
    timeout = getattr(settings, 'thread_timeout', 3)
    pool = ThreadPool(num_threads, timeout)
    m_tasks = []
    for o in args:
        m_tasks.append(MTask(cbfunc, **o))

    for task in m_tasks:
        pool.add_task(task.send)

    pool.wait_completion()
    return m_tasks