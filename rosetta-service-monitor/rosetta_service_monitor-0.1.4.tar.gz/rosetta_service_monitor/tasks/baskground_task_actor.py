#!/usr/bin/env python  
# -*- coding:utf-8 _*-
""" 
@author: xl
@file: baskground_task_actor.py 
@time:
@contact: 
@site:  
@software: PyCharm 
"""
import asyncio
import threading
from queue import Queue
from threading import Event, Thread
from traceback import format_exc

from loguru import logger


class ActorExit(Exception):
    pass


class Actor:
    _instance_lock = threading.Lock()

    def __init__(self):
        self._mailbox = Queue()
        self.start()

    def __new__(cls, *args, **kwargs):
        if not hasattr(Actor, "_instance"):
            with Actor._instance_lock:
                if not hasattr(Actor, "_instance"):
                    Actor._instance = super(Actor, cls).__new__(cls, *args, **kwargs)
        return Actor._instance

    def send(self, msg):
        """
        Send a message to the actor
        """
        self._mailbox.put(msg)

    def recv(self):
        """
        Receive an incoming message
        """
        msg = self._mailbox.get()
        if msg is ActorExit:
            raise ActorExit()
        return msg

    def close(self):
        """
        Close the actor, thus shutting it down
        """
        self.send(ActorExit)

    def start(self):
        """
        Start concurrent execution
        """
        self._terminated = Event()
        t = Thread(target=self._bootstrap)

        t.daemon = True
        t.start()

    def _bootstrap(self):
        try:
            self.run()
        except ActorExit:
            pass
        finally:
            self._terminated.set()

    def join(self):
        self._terminated.wait()

    def run(self):
        """
        Run method to be implemented by the user
        """
        while True:
            msg = self.recv()


class Result:
    def __init__(self):
        self._evt = Event()
        self._result = None

    def set_result(self, value):
        self._result = value

        self._evt.set()

    def result(self):
        self._evt.wait()
        return self._result


class BackgroundWorker(Actor):
    def submit(self, func, *args, **kwargs):
        r = Result()
        self.send((func, args, kwargs, r))
        return r

    def run(self):
        while True:
            func, args, kwargs, r = self.recv()
            resp = None
            if asyncio.iscoroutinefunction(func):
                try:
                    asyncio.run(func(*args, **kwargs))
                except Exception as err:
                    info = f'{err.__class__.__name__}:{err}\n{format_exc()}\n'
                    logger.warning(info)
            else:
                try:
                    resp = func(*args, **kwargs)
                except Exception as err:
                    info = f'{err.__class__.__name__}:{err}\n{format_exc()}\n'
                    logger.warning(info)
            r.set_result(resp)
