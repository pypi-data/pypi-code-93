import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(process)d-%(processName)s - %(filename)s-%(funcName)s[line:%(lineno)d] - %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename='notejob.log',
    filemode='a')


def get_lapse_time(run_time):
    gap_h = run_time // 3600
    gap_m = (run_time % 3600) // 60
    gap_s = (run_time % 3600) % 60
    if gap_h > 0:
        gap_time = "%dh%dm%.5fs" % (gap_h, gap_m, gap_s)
    elif gap_m > 0:
        gap_time = "%dm%.5fs" % (gap_m, gap_s)
    else:
        gap_time = "%.5fs" % gap_s

    return gap_time


class LogTool:
    def __init__(self):
        self.logger = logging.getLogger("nm_flow")
        self.logger.setLevel(logging.DEBUG)

        self.record_msg = ""
        self.record_time = time.time()
        self.record_level = 'none'

    def start(self):
        self._reset_time("start", level='none')

    def _reset_time(self, msg, level):
        self.record_msg = msg
        self.record_time = time.time()
        self.record_level = level

    def _log_run(self, level, msg, run_time=None, *args, **kwargs):
        if run_time is not None:
            msg = '{}, cost time {}.'.format(msg, get_lapse_time(run_time))

        if level == 'debug':
            self.logger.debug(msg, *args, **kwargs)
        if level == 'info':
            self.logger.info(msg, *args, **kwargs)
        if level in ('warning', 'warn'):
            self.logger.warning(msg, *args, **kwargs)
        if level == 'error':
            self.logger.error(msg, *args, **kwargs)

    def run(self, level, msg, record=False, before=False, *args, **kwargs):
        if before:
            run_time = time.time() - self.record_time
            self._log_run(level, msg, run_time, *args, **kwargs)
            self._reset_time(msg, level)

        elif record:
            run_time = time.time() - self.record_time
            self._log_run(self.record_level, self.record_msg,
                          run_time, *args, **kwargs)
            self._reset_time(msg, level)
            self._log_run(level, msg, *args, **kwargs)

        else:
            self._log_run(level, msg, *args, **kwargs)

    def debug(self, msg, record=True, before=False, *args, **kwargs):
        self.run('debug', msg, record=record, before=before, *args, **kwargs)

    def info(self, msg, record=True, before=False, *args, **kwargs):
        self.run('info', msg, record=record, before=before, *args, **kwargs)

    def warn(self, msg, record=True, before=False, *args, **kwargs):
        self.run('warn', msg, record=record, before=before, *args, **kwargs)

    def warning(self, msg, record=True, before=False, *args, **kwargs):
        self.run('warning', msg, record=record, before=before, *args, **kwargs)

    def error(self, msg, record=True, before=False, *args, **kwargs):
        self.run('error', msg, record=record, before=before, *args, **kwargs)

    def setLevel(self, level):
        self.logger.setLevel(level)


def log(name=None) -> logging.Logger:
    _log = logging.getLogger(name)
    return _log


def load_log(name=None) -> logging.Logger:
    _log = logging.getLogger(name)
    return _log


logger = logging.getLogger("")
log_tool = LogTool()
