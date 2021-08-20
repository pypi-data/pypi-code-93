from typing import Optional
from uuid import UUID

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from base64 import b64decode, b64encode

from cryptoshred.backends import KeyBackend
from cryptoshred.exceptions import KeyNotFoundException


class CryptoEngine:
    """
    The base class for CryptoEngines. This exists for typing and documentation purposes.
    """

    def encrypt(
        self, *, data: bytes, key_id: UUID, iv: Optional[bytes] = None
    ) -> bytes:
        """
        Encrypt a piece of data.

        Args:
            data (bytes): The data to encrypt
            key_id (UUID): The uuid of the key used for encryption. Will be looked up in the key backend
            iv (Optional[bytes]): The initialization vector. Will be looked up in the key backend if not provided

        Returns:
            The encrypted value
        """
        raise NotImplementedError()

    def decrypt(
        self, *, cipher_text: bytes, key_id: UUID, iv: Optional[bytes] = None
    ) -> bytes:
        """
        Decrypts a given value

        Args:
            cipher_text (bytes): The ciphertext to decrypt
            key_id (UUID): The uuid of the key used for encryption. Will be looked up in the key backend
            iv (Optional[bytes]): The initialization vector. Will be looked up in the key backend if not provided

        Returns:
            The decrypted value
        """
        raise NotImplementedError()

    def generate_key(self) -> UUID:
        """
        Generates a new cryptographic key and stores it in the key backend

        Returns:
            The id of the newly created key
        """
        raise NotImplementedError()


class AesEngine(CryptoEngine):
    """
    Implements an engine for the AES algorithm in CBC mode.

    Args:
        key_backend (KeyBackend): The key backend
    """

    def __init__(self, key_backend: KeyBackend) -> None:
        self.key_backend = key_backend

    def encrypt(
        self, *, data: bytes, key_id: UUID, iv: Optional[bytes] = None
    ) -> bytes:

        if not iv:
            iv = self.key_backend.get_iv()

        _, key = self.key_backend.get_key(key_id)

        algo = algorithms.AES(key=key)
        cipher = Cipher(algorithm=algo, mode=modes.CBC(iv))
        padder = padding.PKCS7(algo.block_size).padder()

        encryptor = cipher.encryptor()
        padded_data = padder.update(data) + padder.finalize()

        ct = encryptor.update(padded_data) + encryptor.finalize()
        return b64encode(ct)

    def decrypt(
        self, *, cipher_text: bytes, key_id: UUID, iv: Optional[bytes] = None
    ) -> bytes:

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
        res: bytes = padder.update(dt) + padder.finalize()
        return res

    def generate_key(self) -> UUID:
        return self.key_backend.generate_key()
