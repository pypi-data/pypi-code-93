from __future__ import annotations

import os
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any, Collection, Mapping, Optional

# https://packaging.python.org/guides/creating-and-discovering-plugins/#using-package-metadata
# The “selectable” entry points were introduced in importlib_metadata 3.6 and Python 3.10.
# Prior to those changes, entry_points accepted no parameters and always returned a dictionary of entry points
if sys.version_info < (3, 10):
    from importlib_metadata import entry_points, version
else:
    from importlib.metadata import entry_points, version

if TYPE_CHECKING:
    from .query.session import QuerySession

PLUGINS_ENVIRONMENT_VARIABLE = "ATOTI_PLUGINS"
"""Comma separated list of plugins to activate.

For instance: ``"aws,kafka"``.

If ``None``, all installed plugins will be activated.
"""


class Plugin(ABC):
    """Atoti Plugin."""

    @abstractmethod
    def static_init(self):
        """Init called once when the plugin module is imported.

        It can be used to monkey patch the public API to plug the real functions.
        """

    @abstractmethod
    def get_jar_path(self) -> Optional[Path]:
        """Return the path to the JAR."""

    @abstractmethod
    def init_session(self, session: Any):
        """Init called every time a session is created.

        It can be used to call some internal Java function to initialize the plugin.
        """

    @abstractmethod
    def init_query_session(self, query_session: QuerySession):
        """Init called every time a query session is created.

        It can be used to call Python functions to initialize the plugin.
        """


class MissingPluginError(ImportError):
    """Error thrown when a plugin is missing."""

    def __init__(self, plugin_key: str):
        plugin_name = f"atoti-{plugin_key}"
        message = f"The {plugin_name} plugin is missing, install it and try again."
        super().__init__(message)


def _find_active_plugins(
    keys_of_plugins_to_activate: Optional[Collection[str]] = None,
) -> Mapping[str, Plugin]:
    """Find the active plugins."""
    atoti_version = version("atoti")
    plugins = {}
    for entry_point in entry_points(group="atoti.plugins"):
        if (
            keys_of_plugins_to_activate is None
            or entry_point.name in keys_of_plugins_to_activate
        ):
            plugin_package_name = f"atoti-{entry_point.name}"
            plugin_version = version(plugin_package_name)
            if atoti_version != plugin_version:
                raise RuntimeError(
                    f"Cannot load plugin {plugin_package_name} v{plugin_version} because it does not have the same version as atoti (v{atoti_version})."
                )
            plugin_class = entry_point.load()
            plugins[entry_point.name] = plugin_class()

    return plugins


_ACTIVE_PLUGINS: Optional[Mapping[str, Plugin]] = None


def get_active_plugins() -> Mapping[str, Plugin]:
    """Return all the active plugins."""
    global _ACTIVE_PLUGINS  # pylint: disable=global-statement

    if _ACTIVE_PLUGINS is None:
        _ACTIVE_PLUGINS = _find_active_plugins(
            os.environ[PLUGINS_ENVIRONMENT_VARIABLE].split(",")
            if PLUGINS_ENVIRONMENT_VARIABLE in os.environ
            else None
        )

    return _ACTIVE_PLUGINS


def is_plugin_active(plugin_key: str) -> bool:
    """Return whether the plugin is active or not."""
    return plugin_key in get_active_plugins()


def register_active_plugins():
    """Register all the active plugins."""
    for plugin in get_active_plugins().values():
        plugin.static_init()


def ensure_plugin_active(plugin_key: str):
    if not is_plugin_active(plugin_key):
        raise MissingPluginError(plugin_key)
