import collections
import dataclasses
import statistics
from typing import Any, Tuple, Optional, List
import json
import pykka
from datetime import timezone, datetime
import math

import time
import queue
import threading

from retriever_research.ticker import Ticker
from retriever_research.profiler import collectors
from retriever_research.profiler.actors import ProfilerActor, ProfileWriteActor, ProfilerTicker


# CPU usage - per CPU
# CPU usage - average
# available memory
# network throughput up
# network throughput down
# disk io
# disk read throughput
# disk write throughput





class Profiler:
    def __init__(self, file_loc="retriever.profile", interval=0.1):
        self.file_loc = file_loc
        self.interval = interval
        self.profile_writer_ref = None  # type: Optional[pykka.ActorRef]
        self.profiler_ref = None  # type: Optional[pykka.ActorRef]
        self.profiler_ticker = None  # type: Optional[Ticker]
        self.start_time = None  # type: Optional[float]
        self.end_time = None  # type: Optional[float]

    def start(self):
        self.profile_writer_ref = ProfileWriteActor.start(file_loc=self.file_loc)
        self.profiler_ref = ProfilerActor.start(writer_ref=self.profile_writer_ref)
        self.profiler_ticker = ProfilerTicker(profiler_actor_ref=self.profiler_ref, interval=self.interval)
        self.profiler_ticker.start()
        self.start_time = time.time()

    def end(self):
        self.end_time = time.time()
        self.profiler_ticker.stop()
        self.profiler_ticker.join()

        self.profiler_ref.stop(block=True)
        self.profile_writer_ref.stop(block=True)





if __name__ == '__main__':
    prof = Profiler(interval=0.1)
    prof.start()

    dur = 600
    for i in range(dur):
        if i % 10 == 0:
            print(f"{i} of {dur}")
        time.sleep(1)
    time.sleep(600)
    prof.end()

