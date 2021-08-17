from dataclasses import dataclass
from typing import Any, List, Optional

from .storages import BaseStorage, ENVStorage, VaultStorage

__all__ = ["Secrets", "BaseStorage", "VaultStorage", "ENVStorage"]


@dataclass
class Secrets:
    storages: List[BaseStorage]

    def get(self, name: str, fallback_value: Optional[Any] = None) -> Any:
        for storage in self.storages:
            if not storage.enabled:
                continue

            secret = storage.get_secret(name, fallback_value)
            if not secret:
                raise ValueError(f"Secret: '{name}' is not found in '{storage.name}' storage")

            return secret

        raise ValueError(f"Not found available storage for secret: '{name}'.")
