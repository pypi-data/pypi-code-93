from __future__ import annotations

from typing import Dict, Tuple, Any, Callable, List, Optional
from flask import Flask, current_app
import json
import hashlib
import logging
import os
import sys
from daemons import daemonizer

logger = logging.getLogger(__name__)

# logging.basicConfig(
#     level=logging.DEBUG,
#     format='[%(levelname).1s %(asctime).19s] %(message)s',
#     datefmt='%y-%m-%d %H:%M:%S'
# )

class Daemon:
    """An object to represent a daemon.

    Arguments:
        func: the function to run
        minute, hour, day, month, day_of_week: The same as crontab schedule definitions,
            if not given, '*' is implied.
        args: An tuple of positional arguments passed to func.
        kwargs: A dict of keyword arguments passed to func.
    """

    def __init__(
        self,
        func: Callable,
        app: Flask,
        *,
        name: str,
        user: str,
        group: str,
        description: str,
        logfile: str,
        args: Tuple[Any, ...],
        kwargs: Dict[str, Any]
    ) -> None:
        self.func = func
        self.app = app
        self.name = name
        self.user = user
        self.group = group
        self.description = description
        self.args = args
        self.kwargs = kwargs
        self.func_ident = "{func.__module__}:{func.__name__}".format(func=func)
        self.pidfile = os.path.join("/tmp", f"{self.hash}.pid")
        self.logfile = logfile or os.path.join("/tmp", f"{self.hash}.log")
        self.daemon = daemonizer.run(pidfile=self.pidfile)(self.run)

    def start(self):
        self.daemon()
        return self
    
    def stop(self):
        self.daemon.stop()
        return self

    @property
    def hash(self) -> str:
        data = {
            "name": self.func_ident,
            "args": self.args,
            "kwargs": self.kwargs,
        }
        j = json.JSONEncoder(sort_keys=True).encode(data)
        h = hashlib.md5(j.encode("utf-8")).hexdigest()
        return h

    def run(self) -> None:
        try:
            logging.basicConfig(
                filename=self.logfile,
                level=logging.DEBUG,
                format='[%(levelname).1s %(asctime).19s] %(message)s',
                datefmt='%y-%m-%d %H:%M:%S'
            )
            self.func(*self.args, **self.kwargs)
            logger.info("Func is not loop: %s", self.func_ident)
        except Exception:
            logger.exception(
                "Failed to complete daemon at %s", self.func_ident)
        
        self.stop()

    # def as_script_line(self) -> str:

    #     flask_bin = sys.executable + " " + \
    #         self.app.config.get("DAEMON_BIN", " -m flask bws-daemon").strip()
        
    #     env_prefix = (
    #         "FLASK_APP={} ".format(os.getenv("FLASK_APP"))
    #         if os.getenv("FLASK_APP")
    #         else ""
    #     )
        
    #     line = "{} cd {} && {} {} run {}  # {}".format(
    #         self.schedule,
    #         os.getcwd(),
    #         env_prefix,
    #         flask_bin,
    #         self.hash,
    #     )
    #     return line
    
    # def template(self):
    #     """
    #         docstring
    #     """
    #     script = self.as_script_line()
    #     description = "bws-daemon: [{} ({})] {}" % (current_app.name, self.func_ident, self.description)
    #     template = [
    #         "[Unit]",
    #         f"Description={description}",
    #         "After=mongodb.target",

    #         "[Service]",
    #         f"User={self.user}",
    #         f"Group={self.group}",
    #         f"WorkingDirectory={os.getcwd()}"
    #         f"ExecStart={script}",
    #         "# file size",
    #         "LimitFSIZE=infinity",
    #         "# cpu time",
    #         "LimitCPU=infinity",
    #         "# virtual memory size",
    #         "LimitAS=infinity",
    #         "# open files",
    #         "LimitNOFILE=64000",
    #         "# processes/threads",
    #         "LimitNPROC=64000",
    #         "# locked memory",
    #         "LimitMEMLOCK=infinity",
    #         "# total threads (user+kernel)",
    #         "TasksMax=infinity",
    #         "TasksAccounting=false",

    #         "[Install]",
    #         "WantedBy=multi-user.target",
    #     ]

    #     return template
