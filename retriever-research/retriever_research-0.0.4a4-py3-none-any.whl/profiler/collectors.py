import time
from datetime import datetime, timezone
import psutil
from typing import List, Tuple

GIGA = 1_000_000_000
MEGA = 1_000_000


class ThroughputTracker:
    def __init__(self, name: str, multiplier: float = 1.0):
        self.name = name
        self.multiplier = multiplier  # Adjust output unit
        self.last_measured_time = time.time()
        self.last_measured_val = 0.0

    def add_measurement(self, new_val: float, log=False) -> float:
        """
        Add a new value and return the throughput since the last measurement. The Measurement from
        the first call to add() is meaningless since the starting value is arbitrarily set to 0.
        """
        now = time.time()
        timestamp = datetime.fromtimestamp(now, timezone.utc)
        dur = (now - self.last_measured_time)
        delta = (new_val - self.last_measured_val)
        old_last_measured_val = self.last_measured_val

        val_per_sec = (new_val - self.last_measured_val) / (now - self.last_measured_time)
        self.last_measured_time = now
        self.last_measured_val = new_val
        throughput = val_per_sec * self.multiplier
        if log:
            print(new_val, old_last_measured_val, dur, delta, throughput)
        return throughput


class SimpleCpuUtilCollector:
    @staticmethod
    def sample() -> float:
        return psutil.cpu_percent()

class DetailedCpuUtilCollector:
    @staticmethod
    def sample() -> List[float]:
        per_cpu = psutil.cpu_percent(percpu=True)
        return per_cpu

class FreeMemoryCollector:
    @staticmethod
    def sample() -> float:
        free_mem_bytes = psutil.virtual_memory().available
        return free_mem_bytes / GIGA


class ProcInfoCollector:
    @staticmethod
    def sample(log_access_denied=True) -> Tuple[float, int]:
        # Returns memory_used, proc_count
        this_process = psutil.Process()
        proc_count = 1
        proc_mem_used = this_process.memory_info().rss
        for child in this_process.children(recursive=True):
            try:
                proc_count += 1
                proc_mem_used += child.memory_info().rss
            except psutil.NoSuchProcess:
                pass
            except psutil.AccessDenied:
                if log_access_denied:
                    print(f"[Profiler.ProcInfoCollector] AccessDenied when retrieving process info for child ({child}). Ignoring error.")
        return proc_mem_used / MEGA, proc_count


class NetThroughputCollector:
    def __init__(self) -> None:
        self.sent_throughput = ThroughputTracker("Network Sent (Gbit/s)", multiplier=8 / GIGA)
        self.recv_throughput = ThroughputTracker("Network Recv (Gbit/s)", multiplier=8 / GIGA)

        # Discard initial batch that is meaningless
        net = psutil.net_io_counters()
        self.sent_throughput.add_measurement(net.bytes_sent)
        self.recv_throughput.add_measurement(net.bytes_recv)

    def sample(self) -> Tuple[float, float]:
        net = psutil.net_io_counters()
        sent = self.sent_throughput.add_measurement(net.bytes_sent)
        recv = self.recv_throughput.add_measurement(net.bytes_recv)
        return sent, recv


class DiskReadWriteRateCollector:
    def __init__(self) -> None:
        self.read_throughput_tracker = ThroughputTracker("Disk Read (Megabytes/s)", multiplier=1/MEGA)
        self.write_throughput_tracker = ThroughputTracker("Disk Write (Megabytes/s)", multiplier=1/MEGA)
        self.iops = ThroughputTracker("Disk IOPS")

        # Discard initial batch that is meaningless
        disk = psutil.disk_io_counters()
        self.read_throughput_tracker.add_measurement(disk.read_bytes)
        self.write_throughput_tracker.add_measurement(disk.write_bytes)
        self.iops.add_measurement(disk.read_count + disk.write_count)

    def sample(self) -> Tuple[float, float, float]:
        """Return tuple of (Read, Write, IOPS) values"""
        disk = psutil.disk_io_counters()

        read_throughput = self.read_throughput_tracker.add_measurement(disk.read_bytes)
        write_throughput = self.write_throughput_tracker.add_measurement(disk.write_bytes)
        iops = self.iops.add_measurement(disk.read_count + disk.write_count, log=False)
        # print(disk.read_count + disk.write_count, iops)
        return read_throughput, write_throughput, iops
