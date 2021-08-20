from typing import Any, Optional
from uuid import UUID
from cryptoshred.backends import KeyBackend

from cryptoshred.entities import CryptoContainer, container_for
from cryptoshred.exceptions import KeyNotFoundException


def encrypt_value(
    *, value: Any, key_backend: KeyBackend, sid: Optional[UUID] = None
) -> CryptoContainer:
    if sid:
        try:
            key_backend.get_key(sid)
        except KeyNotFoundException:
            raise
    else:
        sid = key_backend.generate_key()

    return container_for(value, id=sid, key_backend=key_backend)
