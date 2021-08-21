from __future__ import annotations


from typing import Dict, Tuple, Any, Callable, List, Optional
from flask import Flask, current_app
import os
import sys
import subprocess


# if TYPE_CHECKING:
from bws_daemon.daemon import Daemon

COMMENT = "bws-daemon"

def _ensure_extension_object():
    obj = current_app.extensions.get("daemon")
    if not obj:
        raise RuntimeError(
            "bws-daemon extension is not registered yet. Please call "
            "'DaemonManager(app)' or 'dm.init_app(app)' before using."
        )
    return obj


class _Manager:

    def __init__(self, *, verbose: bool = True):
        self.verbose = verbose
        self.settings = current_app.config.get_namespace("DAEMON_")
    
    @property
    def daemons(self):
        return _ensure_extension_object().daemons

    def start_daemons(self) -> None:
        """
            Iniciar todos los Procesos
        """
        for daemon in self.daemons:
            print("start daemon: {} name: {}".format(
                daemon.func_ident, daemon.name))
            subprocess.run(
                [sys.executable, sys.argv[0], "start", f"{daemon.name}@{daemon.hash}"],
                # stdout=subprocess.PIPE
            )

    def stop_daemons(self) -> None:
        """
            Parar todos los Procesos
        """
        for daemon in self.daemons:
            print("stop daemon: {} name: {}".format(
                daemon.func_ident, daemon.name))
            subprocess.run(
                [sys.executable, sys.argv[0], "stop", daemon.name],
                # stdout=subprocess.PIPE
            )

    def show_daemons(self) -> None:
        """
            Mostrar todos los Procesos.
        """
        print("Lista de daemons:")
        for daemon in self.daemons:
            is_on = os.path.exists(daemon.pidfile)
            print("[{}] daemon: {} name: {}, active: [{}]".format(
                daemon.hash, daemon.func_ident, daemon.name, 
                ["OFF", "ON"][is_on]
            ))
    
    def status_daemon(self, name) -> None:
        daemon = self.__get_daemon_by_name(name)
        is_on = os.path.exists(daemon.pidfile)
        print("[{}] daemon: {} name: {}, active: [{}]".format(
            daemon.hash, daemon.func_ident, daemon.name, 
            ["OFF", "ON"][is_on]
        ))

    def start_daemon(self, name: str) -> None:
        daemon = self.__get_daemon_by_name(name)
        daemon.start()

    def stop_daemon(self, name: str) -> None:
        daemon = self.__get_daemon_by_name(name)
        daemon.stop()
    
    def log_daemon(self, name: str) -> None:
        daemon = self.__get_daemon_by_name(name)
        f = subprocess.Popen(['tail', '-f', daemon.logfile],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while True:
            line = f.stdout.readline()
            print(line.decode("utf-8").strip())
    
    def clear_log_daemon(self, name: str) -> None:
        daemon = self.__get_daemon_by_name(name)
        subprocess.getoutput(f'echo "limpieza" > {daemon.logfile}')
    
    def clear_log_daemons(self) -> None:
        for daemon in self.daemons:
            self.clear_log_daemon(daemon.name)

    def __get_daemon_by_name(self, name):
        name = name.split("@")[0].strip()
        for daemon in self.daemons:
            if daemon.name.strip() == name:
                return daemon
        raise RuntimeError("No job with name %s found." % name)


class DaemonManager:
    def __init__(self, app: Optional[Flask] = None) -> None:
        self.app = app
        self.daemons: List = []
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        # app.config.setdefault("DAEMON_EXECUTABLE", "/usr/bin/crontab")
        app.extensions["daemon"] = self
        self.app = app

    def daemon(
        self,
        name="",
        description="",
        logfile="",
        user: str = os.getenv("USER"),
        group: str = os.getenv("USER"),
        args: Tuple[Any, ...] = (),
        kwargs: Optional[Dict[str, Any]] = None,
    ) -> Callable:
        """
        Register a function as daemon.
        """

        def wrapper(func: Callable) -> Callable:
            dae = Daemon(
                func,
                self.app,
                name=name or func.__name__,
                user=user,
                group=group,
                description=description,
                logfile=logfile,
                args=args,
                kwargs=kwargs or {},
            )
            self.daemons.append(dae)
            return func

        return wrapper
