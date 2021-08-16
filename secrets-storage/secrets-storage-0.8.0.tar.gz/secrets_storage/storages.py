import abc
import os
import typing as t
from dataclasses import dataclass, field

import hvac


class BaseStorage(abc.ABC):
    name: str
    available: bool

    @property
    @abc.abstractmethod
    def enabled(self) -> bool:
        pass

    @abc.abstractmethod
    def get_secret(self, name: str, fallback_value: t.Any = None) -> t.Any:
        pass


@dataclass
class VaultStorage(BaseStorage):
    host: str
    namespace: str
    role: str

    name: str = "vault_storage"
    available: bool = True
    ssl_verify: bool = False

    auth_mount_point: str = "kubernetes"
    auth_token_path: str = "/var/run/secrets/kubernetes.io/serviceaccount/token"

    secrets: t.Dict[str, t.Any] = field(init=False, repr=False)

    def __post_init__(self):
        if not self.enabled:
            self.secrets = {}
        else:
            self.secrets = self._get_secrets()

    def _get_client_token(self, client: hvac.Client) -> str:
        with open(self.auth_token_path) as f:
            sa_token = f.read()

        auth_info = client.auth_kubernetes(
            role=self.role, jwt=sa_token, mount_point=self.auth_mount_point
        )
        client_token = auth_info.get("auth", {}).get("client_token")
        if not client_token:
            raise ValueError("Not found vault token.")

        return str(client_token)

    def _get_secrets(self):
        client = hvac.Client(url=self.host, verify=self.ssl_verify)
        client.token = self._get_client_token(client)
        return client.read(self.namespace).get("data", {})

    @property
    def enabled(self) -> bool:
        return bool(self.available and self.host and self.auth_token_path and self.namespace)

    def get_secret(self, name: str, fallback_value: t.Any = None) -> t.Any:
        return self.secrets.get(name) or fallback_value


@dataclass
class ENVStorage(BaseStorage):
    name: str = "env_storage"
    available: bool = True

    @property
    def enabled(self) -> bool:
        return bool(self.available)

    def get_secret(self, name: str, fallback_value: t.Any = None) -> t.Any:
        return os.getenv(name, fallback_value)
