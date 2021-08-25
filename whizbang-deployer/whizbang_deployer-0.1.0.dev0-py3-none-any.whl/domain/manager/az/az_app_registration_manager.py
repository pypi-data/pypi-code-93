from abc import abstractmethod

from whizbang.domain.manager.az.az_manager_base import IAzManager, AzManagerBase
from whizbang.domain.models.active_directory.app_registration import AppRegistration
from whizbang.domain.repository.az.az_app_registration_repository import IAzAppRegistrationRepository
from whizbang.util import deployment_helpers


class IAzAppRegistrationManager(IAzManager):
    """"""

    @abstractmethod
    def save(self, app_registration: AppRegistration) -> AppRegistration:
        """"""


class AzAppRegistrationManager(AzManagerBase, IAzAppRegistrationManager):
    def __init__(self, repository: IAzAppRegistrationRepository):
        AzManagerBase.__init__(self, repository)
        self._repository: IAzAppRegistrationRepository = self._repository

    def save(self, app_registration: AppRegistration) -> AppRegistration:
        if app_registration.client_secret.value is None:
            pw = deployment_helpers.generate_random_password()
            app_registration.client_secret.value = pw

        return self._repository.create(app_registration)
