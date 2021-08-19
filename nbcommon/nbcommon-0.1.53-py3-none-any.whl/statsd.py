from prometheus_client import Counter, Histogram
import prometheus_client as pd
from enum import Enum

counters = {}
histograms = {}

class MetricType(Enum):
    counter = 1
    histogram = 2


def register(metric_type, name, desc, labels):
    if metric_type == MetricType.counter:
        c = Counter(name, desc, labels)
        counters[name] = c
        return c
    elif metric_type == MetricType.histogram:
        h = Histogram(name, desc, labels)
        histograms[name] = h
        return h
    else:
        raise 'register error: invalid metric type'

def collect():
    s = pd.generate_latest()
    for _,c in counters.items():
        c._metric_init()
    for _,h in histograms.items():
        h._metric_init()
    return s
