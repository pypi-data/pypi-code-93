from datetime import datetime
import dataclasses
from typing import List, Union
try:
    import ujson as json
except ImportError:
    import json

class ProfileEventParseError(Exception):
    pass

@dataclasses.dataclass
class ProfileEvent:
    __slots__ = ["timestamp", "cpu_avg", "per_cpu", "free_mem", "net_sent", "net_recv",
                 "disk_read", "disk_write", "disk_iops", "proc_mem", "proc_count"]
    timestamp: datetime
    cpu_avg: float
    per_cpu: List[float]
    free_mem: float
    net_sent: float
    net_recv: float
    disk_read: float
    disk_write: float
    disk_iops: float
    proc_mem: float
    proc_count: float

    @staticmethod
    def from_json(j: Union[str, dict]):
        if isinstance(j, str):
            j = json.loads(j)

        kwargs = {}
        for field in ProfileEvent.__slots__:
            if field not in j.keys():
                raise ProfileEventParseError(f"JSON is missing field '{field}': {j}")
            val = j[field]
            if field == "timestamp":
                val = datetime.fromisoformat(val)
            kwargs[field] = val

        return ProfileEvent(**kwargs)


if __name__ == '__main__':
    j_str = '''{"timestamp": "2021-08-14T10:05:11.086604+00:00", "cpu_avg": 5.4, "per_cpu": [20.0, 0.0, 25.0, 0.0, 18.2, 0.0, 16.7, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], "free_mem": 52.214767616, "net_sent": 0.0, "net_recv": 7.904750793241801e-05, "disk_read": 0.0, "disk_write": 0.0, "disk_iops": 0.0, "proc_mem": 16.50688, "proc_count": 1}'''
    j_dict = json.loads(j_str)

    p1 = ProfileEvent.from_json(j_str)
    p2 = ProfileEvent.from_json(j_dict)

    print(p1)
