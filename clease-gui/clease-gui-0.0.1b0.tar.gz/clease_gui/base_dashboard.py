from abc import ABC, abstractmethod
from typing import Dict, Any
import clease
from clease_gui import WidgetStyleMixin, AppDataKeys

__all__ = ['BaseDashboard']


class BaseDashboard(WidgetStyleMixin, ABC):
    def __init__(self, app_data: Dict[str, Any], initialize=True):
        """Base class for dashboards.

        :param app_data: Dictionary with application data, which will be passed around
            to all dashboards, and possibly widgets if they need them.
        :param initialize: Bool, toggle whether the ``initialize`` function is called.
            Mainly useful for testing purposes. Should generally be set to True.
        """
        # We make app_data a property, as to protect it, so it's not changed into
        # a new object. Can still be mutated.
        self._app_data = app_data
        # Create access to the constant app data keys through ".KEYS.<some-key>"
        self.KEYS = AppDataKeys
        if initialize:
            self.initialize()

    @property
    def app_data(self) -> Dict[str, Any]:
        """Return the app data"""
        return self._app_data

    def get_cwd(self):
        return self.app_data[self.KEYS.CWD]

    @property
    def dev_mode(self) -> bool:
        """Are we in developer mode?"""
        return self.app_data.get(self.KEYS.DEV_MODE, False)

    @property
    def debug(self) -> bool:
        """Alternative name for dev mode"""
        return self.dev_mode

    def log_error(self, logger, *args, **kwargs) -> None:
        """Log as exception if we're in dev mode, otherwise only log as error"""
        if self.dev_mode:
            logger.exception(*args, **kwargs)
        else:
            logger.error(*args, **kwargs)

    @abstractmethod
    def initialize(self):
        """Initialize any widgets related to the dashboard"""

    @abstractmethod
    def display(self):
        """Display the dashboard"""

    @property
    def settings(self) -> clease.settings.ClusterExpansionSettings:
        try:
            return self.app_data[self.KEYS.SETTINGS]
        except KeyError:
            # Raise a better message
            raise KeyError(
                'No settings present. Create/load a settings object first.')

    def get_db_name(self):
        """Return the DB name form the settings, and prepend the current
        working directory"""
        settings = self.settings
        cwd = self.app_data[self.KEYS.CWD]
        return cwd / settings.db_name
