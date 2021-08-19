"""logging psutil utilities."""
import logging
import re
import statistics

import psutil as ps
from psutil import cpu_percent, virtual_memory

from wpdatautil.dict import dict_str
from wpdatautil.humanfriendly import format_size

log = logging.getLogger(__name__)

_MOUNTPOINT_EXCLUSION_RE = re.compile("^(?:/host)?/(?:System|Volumes|etc|boot|private|proc|run|snap|sys)($|/)")  # "dev" isn't included here as /dev/shm is useful.
# Note: Mountpoints within /host are created by AWS Batch job definitions.


def log_available_hardware() -> None:
    """Log the available hardware resources.

    Sample output:
    The available hardware is: cpu_count_physical=4, cpu_count_logical=8, cpu_freq=2700, cpu_free_quartiles=80%;92%;100%,
    virtual_mem_available=5.8 GiB, swap_mem_free=748.25 MiB, disk_free:/tmp=383.58 GiB, disk_free:/=383.58 GiB, disk_free:/System/Volumes/Data=383.58 GiB,
    disk_free:/private/var/vm=383.58 GiB, disk_free:/Volumes/Recovery=383.58 GiB
    """
    stats = {
        "cpu_count_physical": ps.cpu_count(logical=False),
        "cpu_count_logical": ps.cpu_count(logical=True),
        "cpu_freq": round(ps.cpu_freq().current),
        "cpu_free_quartiles": ";".join(f"{q:.0f}%" for q in statistics.quantiles([100 - p for p in ps.cpu_percent(interval=0.1, percpu=True)] * 2, method="inclusive")),
        "virtual_mem_available": format_size(ps.virtual_memory().available),
        "swap_mem_free": format_size(ps.swap_memory().free),
        **{
            f"disk_free:{mp}": format_size(ps.disk_usage(mp).free)
            for mp in ("/tmp", *(dp.mountpoint for dp in ps.disk_partitions(all=True)))
            if not _MOUNTPOINT_EXCLUSION_RE.match(str(mp))
        },
    }

    log.info(f"The available hardware is: {dict_str(stats)}")


class PsutilFilter(logging.Filter):
    """psutil logging filter."""

    # Usage ref: https://stackoverflow.com/a/61830838/

    def filter(self, record: logging.LogRecord) -> bool:
        """Add contextual information about the currently used CPU and virtual memory percentages into the `psutil` attribute of the given log record.

        An example of the set value is "c18m68", which means that 18% of the system-wide CPU and 68% of the physical memory are in use.
        """
        record.psutil = f"c{cpu_percent():02.0f}m{virtual_memory().percent:02.0f}"  # type: ignore
        return True  # True means don't discard the record.
