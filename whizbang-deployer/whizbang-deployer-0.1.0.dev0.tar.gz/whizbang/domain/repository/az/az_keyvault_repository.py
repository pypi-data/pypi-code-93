import time
from abc import abstractmethod
from whizbang.data.az_cli_context import AzCliContext
from whizbang.domain.models.keyvault.keyvault_access_policy import KeyVaultAccessPolicy
from whizbang.domain.models.keyvault.keyvault_resource import KeyVaultResource
from whizbang.domain.models.keyvault.keyvault_secret import KeyVaultSecret

from whizbang.domain.repository.az.az_repository_base import AzRepositoryBase
from whizbang.domain.repository.az.az_resource_repository_base import IAzResourceRepository, AzResourceRepositoryBase
from whizbang.util.deployment_helpers import timestamp


class IAzKeyVaultRepository(IAzResourceRepository):
    @abstractmethod
    def get(self, resource: KeyVaultResource):
        """"""

    @abstractmethod
    def get_keyvault_secret(self, keyvault: KeyVaultResource, secret_name: str) -> KeyVaultSecret:
        """"""

    @abstractmethod
    def save_keyvault_secret(self, keyvault: KeyVaultResource, secret: KeyVaultSecret) -> KeyVaultSecret:
        """"""

    @abstractmethod
    def set_access_policy(self, keyvault: KeyVaultResource, policy: KeyVaultAccessPolicy):
        """"""

    @abstractmethod
    def _set_keyvault_secret(self, keyvault: KeyVaultResource, secret: KeyVaultSecret, encoding='utf-8'):
        """"""


class AzKeyVaultRepository(AzResourceRepositoryBase, IAzKeyVaultRepository):
    def __init__(self, context: AzCliContext):
        AzRepositoryBase.__init__(self, az_cli_context=context)

    @property
    def _resource_provider(self) -> str:
        return 'keyvault'

    def get(self, resource: KeyVaultResource):
        return self._execute(f'show --resource-group {resource.resource_group_name} --name {resource.resource_name}')

    def create(self, resource: KeyVaultResource):
        keyvault = self.get(resource)
        if keyvault is None:
            print(
                f'creating keyvault {resource.resource_name} in location: {resource.location} '
                f'and resource group: {resource.resource_group_name}')

            keyvault = self._execute(
                f'create'
                f' --resource-group {resource.resource_group_name}'
                f' --name {resource.resource_name}'
                f' --location {resource.location}'
                f' --enabled-for-template-deployment true'
            )

            while keyvault is None:
                time.sleep(10)
                print(timestamp(f'pausing for resource {resource.resource_name} to finish deploying'))

        else:
            print(f'keyvault {resource.resource_name} already exists')
            return keyvault

    def get_keyvault_secret(self, keyvault: KeyVaultResource, secret_name: str) -> KeyVaultSecret:
        result = self._execute(f'secret show --vault-name {keyvault.resource_name} --name {secret_name}')
        if result is not None:
            secret = KeyVaultSecret(key=secret_name, value=result['value'])
            return secret
        return None

    #todo: save logic should move to manager
    def save_keyvault_secret(self, keyvault: KeyVaultResource, secret: KeyVaultSecret) -> KeyVaultSecret:
        if secret.overwrite is False:
            existing_secret = self.get_keyvault_secret(keyvault, secret.key)
            if existing_secret is not None:
                print(f'secret {secret.key} already exists, overwrite set to "False"')
                return existing_secret

        saved_secret = self._set_keyvault_secret(keyvault, secret)
        return saved_secret

    def set_access_policy(self, keyvault: KeyVaultResource, policy: KeyVaultAccessPolicy):
        secret_permissions = self._handle_permissions_list(policy.permissions.secrets)
        certificate_permissions = self._handle_permissions_list(policy.permissions.certificates)
        key_permissions = self._handle_permissions_list(policy.permissions.keys)
        storage_permissions = self._handle_permissions_list(policy.permissions.storage)

        print(f'attempting to set key vault access policy for {policy.name}')

        access_policy = self._execute(
            f'set-policy -n {keyvault.resource_name}'
            f' --object-id {policy.object_id}'
            f' --certificate-permissions {certificate_permissions}'
            f' --key-permissions {key_permissions}'
            f' --secret-permissions {secret_permissions}'
            f' --storage-permissions {storage_permissions}'
        )

        access_policy_identifier = policy.object_id.lower()
        return access_policy_identifier

    def _set_keyvault_secret(self, keyvault: KeyVaultResource, secret: KeyVaultSecret, encoding='utf-8'):
        if secret.value is None or secret.value == '':
            print(f'Skipping unspecified secret for key: {secret.key} - secret cannot be null or empty')
            # todo: log
            return None

        print(f'setting secret {secret.key} for vault: {keyvault.resource_name}')
        # secure_string = secret.value.encode()
        secret = self._execute(
            f'secret set --vault-name {keyvault.resource_name}'
            f' --name {secret.key} --value {secret.value} --encoding {encoding}')
        # todo: log
        return secret

    @staticmethod
    def _handle_permissions_list(permissions: list) -> str:
        return ' '.join(permissions) if permissions else ""
