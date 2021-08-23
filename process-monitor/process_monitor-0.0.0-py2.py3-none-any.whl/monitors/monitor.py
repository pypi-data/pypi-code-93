import datetime as dt
import functools
import json
import logging

from ..reader import Reader

logger = logging.getLogger('process_monitor')


class Monitor:
    _redis_hash_map_prefix = "process_monitor"

    def __init__(self, redis_client=None):
        self.redis_client = redis_client
        self._thread = None
        self._process_name = None
        self._signal_every = None
        self._received_records = 0
        self._signals_thread_running = False
        self._info = None
        self._start_date = None
        self._asyncio_event_loop = None

    def get_event_loop(self):
        """Create or re-use asyncio event loop."""
        import asyncio
        if self._asyncio_event_loop is None:
            self._asyncio_event_loop = asyncio.get_event_loop()
        return self._asyncio_event_loop

    def get_hash_name(self):
        """Get redis hash map name baed on prefix and process name"""
        return "%s_%s" % (self._redis_hash_map_prefix, self._process_name)

    def _send_signal(self):
        """Send signal with info to redis."""
        pipe = self.redis_client.pipeline()
        pipe.hset(self.get_hash_name(), 'last_signal', str(dt.datetime.now()))
        pipe.hset(self.get_hash_name(), 'info', json.dumps(self.info))
        pipe.execute()
        logger.debug("dispatching signal as [%s]" % self._process_name)

    def _send_signals(self):
        """send signal every N seconds. runs in a thread."""
        import time
        while True:
            self._send_signal()
            time.sleep(self._signal_every)

    def set_uptime(self):
        self.redis_client.hset(self.get_hash_name(), 'start_date', self._start_date.isoformat())

    def run_signals_worker(self, process_name: str, signal_every: int = 10):
        """Dispatch signals every N seconds in a thread.
        :param process_name:
        :param signal_every: a positive int in seconds
        :return:
        """
        import threading
        assert self._signals_thread_running is not True, ".run_signals_worker can be called at most once per monitor."
        assert type(process_name) is str, "expected process_name of type %s but got %s" % (str, type(process_name))
        assert type(signal_every) is int, "expected signal_every of type %s but got %s" % (int, type(signal_every))
        assert signal_every > 0, "signal_every must be greater than 0"
        self._start_date = dt.datetime.now()
        self._process_name = process_name.replace(" ", "_")
        self._signal_every = signal_every
        self.init_info()
        self.set_uptime()
        self._thread = threading.Thread(target=self._send_signals, daemon=True)
        self._thread.start()
        self._signals_thread_running = True

    def init_info(self):
        self.info = json.loads(self.redis_client.hget(self.get_hash_name(), 'info') or '{}')

    @property
    def info(self):
        return self._info

    @info.setter
    def info(self, value):
        assert type(value) is dict, "expected info of type %s but got %s" % (dict, type(value))
        self._info = value
