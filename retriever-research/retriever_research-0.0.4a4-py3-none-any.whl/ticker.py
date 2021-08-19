import queue
import threading

import pykka
from typing import List, Union
from retriever_research.shared_memory import SharedMemory
import time

# Class to run code every X seconds. This type of work doesn't fit well into the pykka actor model.
# This should generally be used to send a message to an actor every X second and have the logic
# exist inside that actor.
class Ticker(threading.Thread):
    def __init__(self, mem: SharedMemory=None, interval=10) -> None:
        self.shutdown_queue = queue.Queue()
        self.interval = interval
        self.mem = mem
        super().__init__()

    def stop(self):
        self.shutdown_queue.put(None)

    def execute(self):
        print(time.time())

    def run(self):
        self.next_scheduled_time = time.time()
        while True:
            try:
                wait_time = max(0.0, self.next_scheduled_time - time.time())
                msg = self.shutdown_queue.get(block=True, timeout=wait_time)
                # Receive a shutdown message
                print(f"Ticker ({self.__class__.__name__}) shutting down")
                return
            except queue.Empty:
                self.next_scheduled_time = time.time() + self.interval
                self.execute()

    # TODO: Add logging function for tickers

