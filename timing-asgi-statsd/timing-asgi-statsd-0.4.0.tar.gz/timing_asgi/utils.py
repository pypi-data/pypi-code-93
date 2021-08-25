# Use timer that's not susceptible to time of day adjustments.
try:
    # perf_counter is only present on Py3.3+
    from time import perf_counter as time_now
except ImportError:
    # fall back to using time
    from time import time as time_now

from .interfaces import MetricNamer


class TimingStats(object):
    def __init__(self, name=None):
        self.name = name

    def start(self):
        self.start_time = time_now()

    def stop(self):
        self.end_time = time_now()

    def __enter__(self):
        self.start()
        return self

    @property
    def time(self):
        return self.end_time - self.start_time

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()


class PathToName(MetricNamer):
    def __init__(self, prefix):
        self.prefix = prefix

    def __call__(self, scope):
        path = scope.get("path")[1:]
        return f"{self.prefix}.{path.replace('/', '.')}"
