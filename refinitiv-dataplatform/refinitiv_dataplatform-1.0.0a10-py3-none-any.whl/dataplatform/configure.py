__all__ = ["config"]

import asyncio
import nest_asyncio
import atexit
import json
import os
import os.path
import sys
import re
from json.decoder import WHITESPACE

import logging

import config as ext_config_mod
from eventemitter import EventEmitter
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer

from refinitiv.dataplatform.tools._common import get_from_path


def enable_watch():
    global _observer
    _observer = Observer()
    _event_handler = _RDPConfigChangedHandler(patterns=_config_files_paths)
    _dir_names = {os.path.dirname(f) for f in _config_files_paths}
    [_observer.schedule(_event_handler, dirname) for dirname in _dir_names]
    _observer.start()

    atexit.register(unload)


def unload():
    config.remove_all_listeners()
    if _observer:
        _observer.stop()
        _observer.join()


def _get_filepath(rootdir, filename):
    if rootdir and filename:
        path = os.path.join(rootdir, filename)
        return path


_SUBS_PATTERN = re.compile(r".*?\${(\w+(-\w+)*(_\w+)*(:\w+)*)}.*?")


def _substitute_values(data, root=None):
    if not data:
        return data

    for k, v in data.items():
        if hasattr(v, "get"):
            _substitute_values(v, root)
        elif isinstance(v, str):
            match = _SUBS_PATTERN.findall(v)
            if match:
                for g in match:
                    path = g[0]
                    old = f"${{{path}}}"
                    new = get_from_path(root, path, ":")
                    new = None if isinstance(new, list) else new
                    v = v.replace(old, new or old)
                data[k] = v
    return data


def _read_config_file(path):
    if not os.path.exists(path):
        #   skip reading config file
        logging.getLogger().debug(
            f"WARNING!!! SKIPPING reading config file at {path} because the config file does not exist."
        )
        return {}

    try:
        with open(path, "r") as f:
            data = json.load(f, cls=_JSONDecoder)
    except Exception as e:
        logging.getLogger().error(
            f"ERROR!!! The config file at {path} has error while reading the config file.\n"
            + f"{e!r}"
        )
        sys.exit(-1)

    return _substitute_values(data, data)


def _create_configs(files_paths):
    config_from_dict = ext_config_mod.config_from_dict
    dicts = [_read_config_file(f) for f in files_paths]
    configs = [config_from_dict(d) for d in dicts]
    return configs


def _create_rdpconfig(files_paths):
    configs = _create_configs(files_paths)
    return _RDPConfig(*configs)


class _RDPConfigChangedHandler(PatternMatchingEventHandler):
    def on_any_event(self, event):
        configs = _create_configs(_config_files_paths)
        _new_config = ext_config_mod.ConfigurationSet(*configs)
        if _new_config.as_dict() != config.as_dict():
            config.configs = _new_config.configs
            try:
                config.emit("update")
            except Exception:
                pass


class _JSONDecoder(json.JSONDecoder):
    _ENV_SUBS_PATTERN = re.compile(r".*?\${(\w+)}.*?")

    def decode(self, s, _w=WHITESPACE.match):
        match = self._ENV_SUBS_PATTERN.findall(s)
        if match:
            for g in match:
                s = s.replace(f"${{{g}}}", os.environ.get(g, g))
            s = s.replace("\\", "\\\\")
        return super().decode(s, _w)


class _keys(object):
    endpoints = "endpoints"
    log_level = "logs.level"
    log_filename = "logs.transports.file.name"
    log_file_enabled = "logs.transports.file.enabled"
    log_console_enabled = "logs.transports.console.enabled"
    log_file_size = "logs.transports.file.size"
    log_filter = "logs.filter"
    log_max_files = "logs.transports.file.maxFiles"
    log_interval = "logs.transports.file.interval"
    watch_enabled = "config-change-notifications-enabled"

    desktop_sessions = "sessions.desktop"

    @staticmethod
    def desktop_session(session_name):
        return "sessions.desktop.%s" % session_name

    @staticmethod
    def desktop_base_uri(session_name):
        return "sessions.desktop.%s.base-url" % session_name

    @staticmethod
    def desktop_platform_paths(session_name):
        return "sessions.desktop.%s.platform-paths" % session_name

    @staticmethod
    def desktop_handshake_url(session_name):
        return "sessions.desktop.%s.handshake-url" % session_name

    @staticmethod
    def desktop_endpoints(session_name):
        return "sessions.desktop.%s.endpoints" % session_name

    platform_sessions = "sessions.platform"

    @staticmethod
    def platform_session(session_name):
        return "sessions.platform.%s" % session_name

    @staticmethod
    def platform_endpoints(session_name):
        return "sessions.platform.%s.endpoints" % session_name

    @staticmethod
    def platform_base_uri(session_name):
        return "sessions.platform.%s.base-url" % session_name

    @staticmethod
    def platform_auth_uri(session_name):
        return "sessions.platform.%s.auth.url" % session_name

    @staticmethod
    def platform_token_uri(session_name):
        return "sessions.platform.%s.auth.token" % session_name

    @staticmethod
    def platform_auto_reconnect(session_name):
        return "sessions.platform.%s.auto-reconnect" % session_name

    @staticmethod
    def platform_server_mode(session_name):
        return "sessions.platform.%s.server-mode" % session_name

    @staticmethod
    def platform_realtime_distribution_system(session_name):
        return "sessions.platform.%s.realtime-distribution-system" % session_name

    stream_connects = "streaming.connections"

    @staticmethod
    def stream_connects_locations(session_name):
        return "streaming.connections.%s.locations" % session_name

    @staticmethod
    def stream_connects_type(session_name):
        return "streaming.connections.%s.type" % session_name

    @staticmethod
    def stream_connects_format(session_name):
        return "streaming.connections.%s.format" % session_name


keys = _keys


class _RDPConfig(ext_config_mod.ConfigurationSet):
    keys = _keys

    def __init__(self, *configs):
        super().__init__(*configs)

        try:
            asyncio.get_event_loop()
        except RuntimeError:
            asyncio.set_event_loop(asyncio.new_event_loop())

        nest_asyncio.apply(asyncio.get_event_loop())

        self._emitter = EventEmitter()
        setattr(self, "on", self._emitter.on)
        setattr(self, "remove_listener", self._emitter.remove_listener)
        setattr(self, "remove_all_listeners", self._emitter.remove_all_listeners)
        setattr(self, "emit", self._emitter.emit)


_RDPLIB_ENV = "RDPLIB_ENV"
_RDPLIB_ENV_DIR = "RDPLIB_ENV_DIR"

_config_filename_template = "rdplibconfig.%s.json"

_env_name = os.environ.get(_RDPLIB_ENV, "prod")
_config_filename = _config_filename_template % _env_name
_project_config_dir = os.environ.get(_RDPLIB_ENV_DIR) or os.getcwd()
_config_files_paths = [
    c
    for c in [
        _get_filepath(
            rootdir=_project_config_dir, filename=_config_filename
        ),  # PROJECT_CONFIG_FILE
        _get_filepath(
            rootdir=os.path.expanduser("~"), filename=_config_filename
        ),  # USER_CONFIG_FILE
        _get_filepath(
            rootdir=os.path.dirname(__file__),
            filename=_config_filename_template % "default",
        ),  # DEFAULT_CONFIG_FILE
    ]
    if c
]


logging.getLogger().debug(f"list of reading config file are {_config_files_paths}.")

config = _create_rdpconfig(_config_files_paths)
get = config.get
get_bool = config.get_bool
get_str = config.get_str
get_int = config.get_int

_observer = None
_watch_enabled = config.get_bool(keys.watch_enabled)
if _watch_enabled:
    enable_watch()
