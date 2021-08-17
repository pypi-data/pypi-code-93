from typing import Any, Optional
from uuid import UUID

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from base64 import b64decode, b64encode

from cryptoshred.backends import KeyBackend
from cryptoshred.exceptions import KeyNotFoundException


class CryptoEngine:
    def encrypt(self, *, data: Any, id: UUID, iv: Optional[bytes] = None) -> bytes:
        raise NotImplementedError()

    def decrypt(
        self, *, cipher_text: bytes, key_id: UUID, iv: Optional[bytes] = None
    ) -> Any:
        raise NotImplementedError()

    def generate_key(self) -> UUID:
        raise NotImplementedError()


class AesEngine(CryptoEngine):
    def __init__(self, key_backend: KeyBackend) -> None:
        self.key_backend = key_backend

    def encrypt(
        self, *, data: bytes, id: UUID, iv: Optional[bytes] = None
    ) -> bytes:  # TODO more specific typing.

        if not iv:
            iv = self.key_backend.get_iv()

        _, key = self.key_backend.get_key(id)

        algo = algorithms.AES(key=key)
        cipher = Cipher(algorithm=algo, mode=modes.CBC(iv))
        padder = padding.PKCS7(algo.block_size).padder()

        encryptor = cipher.encryptor()
        padded_data = padder.update(data) + padder.finalize()

        ct = encryptor.update(padded_data) + encryptor.finalize()
        return b64encode(ct)

    def decrypt(
        self, *, cipher_text: bytes, key_id: UUID, iv: Optional[bytes] = None
    ) -> Any:

        _, key = self.key_backend.get_key(key_id)
        if not key:
            raise KeyNotFoundException()
        if not iv:
            iv = self.key_backend.get_iv()

        algo = algorithms.AES(key=key)
        cipher = Cipher(algorithm=algo, mode=modes.CBC(iv))
        padder = padding.PKCS7(algo.block_size).unpadder()

        decryptor = cipher.decryptor()
        ct = b64decode(cipher_text)
        dt = decryptor.update(ct) + decryptor.finalize()
        return padder.update(dt) + padder.finalize()

    def generate_key(self) -> UUID:
        return self.key_backend.generate_key()
