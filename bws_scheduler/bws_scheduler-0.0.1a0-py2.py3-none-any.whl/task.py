from typing import Dict, Tuple, Any, Callable, List, Optional
from datetime import datetime, timedelta
from .utils import str_parse_to_time, is_between_time
import inspect
import time
import logging


logger = logging.getLogger(__name__)


class Task:
    ACTIVE = "active"
    SLEEP = "sleep"
    QUEUE = "queue"
    INITING = "initing"
    ERROR = "error"

    """Task for Schedule"""

    def __init__(self, name=None, sameness=[], cron=None, logger=logger):
        self.logger = logger
        self.cron = cron
        self.name = name or self.get_name()
        self.value_every = None  # timedelta
        self.value_after_at = None  # datetime.time
        self.value_before_at = None  # datetime.time
        self.value_starting_after = None  # datetime.time
        self.sameness = sameness
        self.list_tasks_sameness = None
        self._active_at = datetime.now()
        self.context = {}
        self.state = {}
        self._func = lambda x: x
        self._func_args = ()
        self._func_kwargs = {}
        self._func_is_varkw = False
        self.status = None

        self.info = logger.info
        self.warning = logger.warning
        self.warn = logger.warn
        self.error = logger.error
        self.critical = logger.critical
        self.exception = logger.exception


    @classmethod
    def get_name(cls):
        return cls.__name__

    def __str__(self):
        return self.name

    def init(self):
        pass

    @property
    def active_at(self):
        return self._active_at

    @active_at.setter
    def active_at(self, value):
        self._active_at = value

    def every(self, *args, **kwargs):
        # self.info("%s, %s, %s" % (self.name, str(args), not args and not kwargs))
        if not args and not kwargs:
            self.value_every = None
        elif args and isinstance(args[0], str):
            obj_time = str_parse_to_time(*args)
            self.value_every = timedelta(
                hours=obj_time.hour,
                minutes=obj_time.minute,
                seconds=obj_time.second
            )
        else:
            self.value_every = timedelta(*args, **kwargs)
        return self

    def after_at(self, strtime):
        self.value_after_at = strtime
        return self

    def before_at(self, strtime):
        self.value_before_at = strtime
        return self

    def between(self, after_at, before_at):
        self.value_after_at = after_at
        self.value_before_at = before_at
        return self

    def starting_after(self, hours=0, minutes=0, seconds=0):
        self.value_starting_after = datetime.now() + timedelta(hours=hours,
                                                               minutes=minutes, seconds=seconds)
        return self

    def func(self, func: Callable, *args, **kwargs):
        self._func = func
        self._func_args = args
        self._func_kwargs = kwargs
        self._func_is_varkw = not inspect.getfullargspec(func).varkw is None
        self._func_inspect_args = inspect.getfullargspec(func).args
        return self

    def active(self):
        self.status = Task.ACTIVE
        return self

    def queue(self):
        self.status = Task.QUEUE
        return self

    def run(self, **kwargs):
        try:
            if self._func_is_varkw:
                kwargs.update({"task": self, "cron": self.cron})
            else:
                if "state" in self._func_inspect_args:
                    kwargs.update({
                        "state": self.state,
                    })
                if "context" in self._func_inspect_args:
                    kwargs.update({
                        "context": self.context,
                    })
                if "task" in self._func_inspect_args:
                    kwargs.update({
                        "task": self,
                    })
                if "cron" in self._func_inspect_args:
                    kwargs.update({
                        "cron": self.cron,
                    })

            self._func(*self._func_args, **self._func_kwargs, **kwargs)
        except Exception as e:
            self.logger.exception(e)

        return self.sleep_every()

    def handle_init(self):
        try:
            self.status = Task.INITING
            self.init()
            self.status = Task.SLEEP
        except Exception as e:
            self.logger.exception(e)

    def handle(self, **kwargs):
        try:
            # self.logger.info("handle %s" % self.name)
            self.status = Task.ACTIVE
            self.run(**kwargs)
            self.status = Task.SLEEP
        except Exception as e:
            self.logger.exception(e)
            self.status = Task.ERROR

    def is_between(self):
        now = datetime.now()
        if not self.value_after_at or type(self.value_after_at) is str:
            self.value_after_at = str_parse_to_time(
                self.value_after_at or "00:00:01")
        if not self.value_before_at or type(self.value_before_at) is str:
            self.value_before_at = str_parse_to_time(
                self.value_before_at or "23:59:59")

        return is_between_time(now, self.value_after_at, self.value_before_at)

    def is_available(self):
        if self.value_every is None:
            return False

        if self.status == Task.INITING:
            return False

        if self.status in [Task.QUEUE, Task.ACTIVE]:
            return False

        now = datetime.now()
        if self.value_starting_after:
            if now < self.value_starting_after:
                return False

        if now < self.active_at:
            return False

        if not self.is_between():
            return False

        if self.is_running_sameness():
            return False

        return True

    def is_running_sameness(self):
        if self.sameness:
            # if self.list_tasks_sameness is None:
            self.list_tasks_sameness = []
            for same in self.sameness:
                for t in self.cron._list_tasks:
                    if self != t\
                            and t.sameness\
                            and same in t.sameness:
                        self.list_tasks_sameness.append(t)

            for same in self.sameness:
                for t in self.list_tasks_sameness:
                    if self != t\
                            and t.sameness\
                            and same in t.sameness\
                            and (t.is_active or t.is_queue):
                        # self.active_at = datetime.now() + self.value_every
                        return True
        return False

    def set_context(self, cron, context={}):
        self.cron = cron
        self.context = context
        return self

    def sleep_every(self, **kargs):
        if kargs:
            if kargs.pop("sum", False):
                self.active_at = (
                    datetime.now() + self.value_every) + timedelta(**kargs)
            else:
                self.active_at = datetime.now() + timedelta(**kargs)
        elif not self.value_every is None:
            self.active_at = (datetime.now() + self.value_every)
        return self

    def reset_active_at(self):
        self.active_at = datetime.now()
        return self

    @property
    def is_queue(self):
        return self.status == Task.QUEUE

    @property
    def is_active(self):
        return self.status == Task.ACTIVE

    def close(self):
        self.cron.remove_task(self)

    
