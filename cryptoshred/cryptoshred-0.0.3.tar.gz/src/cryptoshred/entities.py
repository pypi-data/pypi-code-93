from enum import Enum
from functools import singledispatch
import json
from typing import Any, Dict, Generic, Optional, TypeVar

from uuid import UUID, uuid4
from pydantic import BaseModel, UUID4, PrivateAttr
from pydantic.fields import Field
from cryptoshred.backends import KeyBackend

from cryptoshred.engines import AesEngine
from cryptoshred.exceptions import KeyNotFoundException

T = TypeVar("T")
BM = TypeVar("BM", bound=BaseModel)


class CryptographicAlgorithm(str, Enum):
    """
    The available crypto algorithms.
    """

    aes_cbc = "AES"


class CryptoContainer(BaseModel, Generic[T]):
    """
    The CryptoContainer class implements the concept of a cryptoshreddable entity.

    Args:
        id (UUID4): Optional uuid of the key to use for decryption. Generated if not present
        enc (bytes): The encrypted value
        algo (CryptographicAlgorithm): The cryptographic algorithm used. Defaults to AES_CBC
        ksize (int): The key size used
        key_backend (KeyBackend): The backend used to look up keys
    """

    class Config:
        validate_assignment = True
        arbitrary_types_allowed = True  # TODO remove

    id: UUID4 = Field(default_factory=uuid4)
    enc: bytes = b""
    algo: CryptographicAlgorithm = CryptographicAlgorithm.aes_cbc
    ksize: int = 256
    _cached_value: Optional[T] = PrivateAttr(default=None)
    _key_backend: KeyBackend = PrivateAttr(default=None)

    def __init__(self, **data: Dict) -> None:
        super().__init__(**data)
        # TODO default key backend
        self._key_backend = data.get("key_backend")  # type: ignore

    def value(self, clazz: T) -> Optional[T]:
        """
        Will return the contained value constructed using the constructor of the given class.

        Agrs:
            clazz (T): The class to deserialize the value to

        Returns:
            The value contained in the container passed through the constructor of the given class
        """
        if not self._cached_value:
            self._cached_value = self._decrypt(clazz)
        return self._cached_value

    def plain(self) -> str:
        """
        The contained value as string.

        Returns:
            The contained value
        """
        return self.value(str)  # type: ignore

    def _decrypt(self, clazz: T) -> Optional[T]:  # Py3.10 switch
        try:
            # TODO: Engine determination from container
            engine = AesEngine(self._key_backend)
            dt = engine.decrypt(cipher_text=self.enc, key_id=self.id)
            if clazz == str:
                return dt.decode("utf-8")  # type: ignore
            elif clazz == bytes:
                return dt  # type: ignore
            elif clazz == int:
                return int.from_bytes(dt, byteorder="big", signed=True)  # type: ignore
            else:
                try:
                    return clazz(**json.loads(dt))  # type: ignore
                except Exception:
                    return clazz(dt)  # type: ignore
        except KeyNotFoundException:
            return None


@singledispatch
def container_for(
    value: Any, *, id: Optional[UUID] = None, key_backend: KeyBackend
) -> CryptoContainer[Any]:
    """
    Given a value and some configuration will return the cryptocontainer for
    that value. Specific typing is implemented via singledispatch.
    If no specific way to encode the value is available the implementation will
    fallback to calling ``bytes`` on the passed object.

    Args:
        value (T): The value to provide a cryptocontainer for
        id (UUID4): The subject id used to find the key. If ``None`` a new key will be generated
        key_backend (KeyBackend): The key backend to use for persistence

    Returns:
        The cryptocontainer containing the passed value
    """

    data = bytes(value)

    return _encrypt(data=data, id=id, key_backend=key_backend)


@container_for.register
def container_for_str(
    value: str, *, id: Optional[UUID] = None, key_backend: KeyBackend
) -> CryptoContainer[str]:
    """For strings"""

    data = bytes(value, "utf-8")

    return _encrypt(data=data, id=id, key_backend=key_backend)


@container_for.register
def container_for_bytes(
    value: bytes, *, id: Optional[UUID] = None, key_backend: KeyBackend
) -> CryptoContainer[bytes]:
    """For bytes"""

    return _encrypt(data=value, id=id, key_backend=key_backend)


@container_for.register
def container_for_base_model(
    value: BaseModel, *, id: Optional[UUID] = None, key_backend: KeyBackend
) -> CryptoContainer[BaseModel]:
    """For objects extending pydantics BaseModel"""

    data = bytes(value.json(), "utf-8")

    return _encrypt(data=data, id=id, key_backend=key_backend)


@container_for.register
def container_for_dict(
    value: dict, *, id: Optional[UUID] = None, key_backend: KeyBackend
) -> CryptoContainer[dict]:
    """For good old dictionaries"""

    data = bytes(json.dumps(value), "utf-8")

    return _encrypt(data=data, id=id, key_backend=key_backend)


@container_for.register
def container_for_int(
    value: int, *, id: Optional[UUID] = None, key_backend: KeyBackend
) -> CryptoContainer[int]:
    """For integers"""

    data = value.to_bytes((value.bit_length() + 7) // 8, byteorder="big", signed=True)

    return _encrypt(data=data, id=id, key_backend=key_backend)


def _encrypt(
    data: bytes, id: Optional[UUID], key_backend: KeyBackend
) -> CryptoContainer:
    engine = AesEngine(key_backend=key_backend)
    if not id:
        id = engine.generate_key()
    ct = engine.encrypt(data=data, key_id=id)
    return CryptoContainer(enc=ct, key_backend=key_backend, id=id)  # type: ignore
