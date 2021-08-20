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
from retriever_research.profiler.event import ProfileEvent



class ProfilerTick:
    pass


class ProfilerTicker(Ticker):
    def __init__(self, profiler_actor_ref: pykka.ActorRef, interval=1.0) -> None:
        self.shutdown_queue = queue.Queue()
        self.interval = interval
        self.profiler_actor_ref = profiler_actor_ref
        super().__init__(interval=interval)

    def execute(self):
        self.profiler_actor_ref.tell(ProfilerTick())


"""
- SimpleCpuUtilization = Measured in percent
- FreeMemory = Measured in Gigabytes
- NetworkSentThroughput = Measured in Gigabit/s
- NetworkRecvThroughput = Measured in Gigabit/s
- DiskIops
- DiskReadThroughput = Measured in Megabytes/second
- DiskWriteThroughput = Measured in Megabytes/second
- ProcessMemoryUsed = Measured in Megabytes  (includes memory used by subprocesses)
- ProcessCount
"""
class ProfilerActor(pykka.ThreadingActor):
    def __init__(self, writer_ref: pykka.ActorRef, log_access_denied=False):
        super().__init__()
        self.writer_ref = writer_ref
        self.log_access_denied = log_access_denied

    def on_start(self) -> None:
        self.net_throughput_tracker = collectors.NetThroughputCollector()
        self.disk_throughput_tracker = collectors.DiskReadWriteRateCollector()

        # Ignore the first measurement
        self.net_throughput_tracker.sample()
        self.disk_throughput_tracker.sample()
        collectors.SimpleCpuUtilCollector.sample()
        collectors.DetailedCpuUtilCollector.sample()

    def on_receive(self, message: Any) -> Any:
        try:
            timestamp = datetime.now(timezone.utc)

            cpu_avg = collectors.SimpleCpuUtilCollector.sample()
            per_cpu = collectors.DetailedCpuUtilCollector.sample()
            free_mem = collectors.FreeMemoryCollector.sample()
            net_sent, net_recv = self.net_throughput_tracker.sample()
            disk_read, disk_write, disk_iops = self.disk_throughput_tracker.sample()
            proc_mem, proc_count = collectors.ProcInfoCollector.sample(self.log_access_denied)

            profile_event = ProfileEvent(
                timestamp=timestamp,
                cpu_avg=cpu_avg,
                per_cpu=per_cpu,
                free_mem=free_mem,
                net_sent=net_sent,
                net_recv=net_recv,
                disk_read=disk_read,
                disk_write=disk_write,
                disk_iops=disk_iops,
                proc_mem=proc_mem,
                proc_count=proc_count
            )

            self.writer_ref.tell(profile_event)
        except Exception as e:
            print(f"Profiler actor exception during on_receive: {e}")
            raise e
        except KeyboardInterrupt as e:
            print(f"Profiler actor keyboard interrupt during on_receive: {e}")
            raise e


class ProfileWriteActor(pykka.ThreadingActor):
    def __init__(self, file_loc):
        super().__init__()
        self.file_loc = file_loc

    def on_start(self) -> None:
        self.profile_fileobj = open(self.file_loc, "w")

    def on_receive(self, msg: Any) -> Any:
        assert isinstance(msg, ProfileEvent), f"Incorrect message type received, {type(msg)}"
        data = dict(
            timestamp=msg.timestamp.isoformat(),
            cpu_avg=msg.cpu_avg,
            per_cpu=msg.per_cpu,
            free_mem=msg.free_mem,
            net_sent=msg.net_sent,
            net_recv=msg.net_recv,
            disk_read=msg.disk_read,
            disk_write=msg.disk_write,
            disk_iops=msg.disk_iops,
            proc_mem=msg.proc_mem,
            proc_count=msg.proc_count
        )
        as_str = json.dumps(data)
        self.profile_fileobj.write(f"{as_str}\n")

    def on_stop(self):
        self.profile_fileobj.close()

    def on_failure(self, *args):
        print(f"ProfileWriteActor failed, {args[0]}, {args[1]}")
        self.profile_fileobj.close()
