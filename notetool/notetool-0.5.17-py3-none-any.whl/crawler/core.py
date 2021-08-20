import logging
import threading
from queue import Queue
from threading import Thread, Event

from notetool.tool.log import log


class Node(Thread):
    """

    """

    def __init__(self, interval=10, queue_size=2):
        Thread.__init__(self)
        self.logger = log("crawler")
        self.logger.setLevel(logging.INFO)

        self.interval = interval

        self.finished = Event()
        self.queue_list = [Queue() for i in range(0, queue_size)]
        self.total_list = [0 for i in range(0, queue_size)]
        self.inputs = []
        self.outputs = []

    def cancel(self):
        self.finished.set()

    def run(self):
        while not self.finished.is_set():
            try:
                self.job()
            except Exception as e:
                print("job run error {}".format(e))
            self.finished.wait(self.interval)

    def job(self):
        self.logger.debug(
            "{}\t"
            "self:{sel}"
            "active:{active}\t"
            "item:{item}\t".format("job",
                                   sel=self,
                                   active=threading.activeCount(),
                                   item=self.qsize(), ))

    def put(self, obj, index=0, block=True, timeout=1):
        self.queue_list[index].put(obj, block=block, timeout=timeout)

    def get(self, index=0, block=True, timeout=1):
        self.total_list[index] += 1
        return self.queue_list[index].get(block=block, timeout=timeout)

    def qsize(self, index=0):
        return self.queue_list[index].qsize()

    def empty(self, index=0):
        return self.queue_list[index].empty()

    def not_empty(self, index=0):
        return not self.empty(index)

    def total(self, index=0):
        return self.total_list[index]

    def __call__(self, inputs, *args, **kwargs):
        self.inputs = inputs
        return self


class Pool(Node):
    def __init__(self, *args, **kwargs):
        super(Pool, self).__init__(*args, **kwargs)
