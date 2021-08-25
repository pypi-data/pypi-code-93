from abc import abstractmethod

from whizbang.config.app_config import AppConfig
from whizbang.domain.handler.handler_base import IHandler, HandlerBase
from whizbang.domain.manager.az.az_app_registration_manager import IAzAppRegistrationManager
from whizbang.domain.models.active_directory.app_registration import AppRegistration


class IAppRegistrationHandler(IHandler):
    """"""

    @abstractmethod
    def save(self, app_registration: AppRegistration) -> AppRegistration:
        """"""


class AppRegistrationHandler(HandlerBase, IAppRegistrationHandler):
    def __init__(self, app_config: AppConfig, app_registration_manager: IAzAppRegistrationManager):
        HandlerBase.__init__(self, app_config=app_config)
        self.__app_registration_manager = app_registration_manager

    def save(self, app_registration: AppRegistration) -> AppRegistration:
        return self.__app_registration_manager.save(app_registration)
