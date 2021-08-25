from abc import abstractmethod
from typing import Dict, List

from whizbang.config.app_config import AppConfig
from whizbang.config.environment_config import EnvironmentConfig
from whizbang.domain.handler.handler_base import IHandler, HandlerBase
from whizbang.domain.manager.az.az_keyvault_manager import IAzKeyVaultManager
from whizbang.domain.models.keyvault.keyvault_access_policy import KeyVaultAccessPolicy
from whizbang.domain.models.keyvault.keyvault_resource import KeyVaultResource
from whizbang.domain.models.keyvault.keyvault_secret import KeyVaultSecret
from whizbang.util.json_helpers import import_local_json
from whizbang.util.path_defaults import get_solution_directory
from whizbang.util.path_helpers import find_file


class IKeyVaultHandler(IHandler):
    """"""

    @abstractmethod
    def create_keyvault(self, keyvault_name: str, env_config: EnvironmentConfig) -> KeyVaultResource:
        """"""

    @abstractmethod
    def save_keyvault_secrets(self, keyvault: KeyVaultResource, secrets: 'list[KeyVaultSecret]') -> Dict[str, KeyVaultSecret]:
        """"""

    @abstractmethod
    def set_keyvault_access_policies(self, solution_name, env_config: EnvironmentConfig):
        """"""


class KeyVaultHandler(HandlerBase, IKeyVaultHandler):
    def __init__(
            self,
            app_config: AppConfig,
            keyvault_manager: IAzKeyVaultManager
    ):
        HandlerBase.__init__(self, app_config=app_config)
        self.__keyvault_manager = keyvault_manager

    def create_keyvault(self, keyvault_name: str, env_config: EnvironmentConfig) -> KeyVaultResource:
        full_name = f'{env_config.resource_name_prefix}-{keyvault_name}-{env_config.resource_name_suffix}'

        keyvault = KeyVaultResource(
            resource_name=full_name,
            resource_group_name=env_config.resource_group_name,
            location=env_config.resource_group_location
        )

        self.__keyvault_manager.create(keyvault)
        return keyvault

    def save_keyvault_secrets(self, keyvault: KeyVaultResource, secrets: 'list[KeyVaultSecret]') -> Dict[str, KeyVaultSecret]:
        result = self.__keyvault_manager.save_keyvault_secrets(keyvault=keyvault, secrets=secrets)
        return result

    def set_keyvault_access_policies(self, solution_name, env_config: EnvironmentConfig):
        solution_directory = get_solution_directory(self._app_config, solution_name)
        file_path = find_file('keyvault_access_policies.json', solution_directory)
        if file_path is None:
            print('no keyvault_access_policies.json found, skip setting keyvault access policies')
            return

        keyvault_json = import_local_json(file_path)

        keyvaults = keyvault_json['keyvaults']

        for keyvault_obj in keyvaults:
            policies = list(map(lambda x: KeyVaultAccessPolicy(**x), keyvault_obj['acls']))

            keyvault = KeyVaultResource(
                resource_name=f'{env_config.resource_name_prefix}-{keyvault_obj["name"]}-{env_config.resource_name_suffix}',
                resource_group_name=env_config.resource_group_name,
                location=env_config.resource_group_location
            )

            self.__keyvault_manager.set_access_policies(keyvault=keyvault, policies=policies)
