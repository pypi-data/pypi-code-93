'''
psypher.cipher - Symmetric ciphers which uses shared secret to encrypt data.
'''

from abc import ABCMeta, abstractmethod
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers import aead
from .secret import SymmetricKey, Ciphertext
from . import errors, Error
import os

__all__ = ['IEncryptor', 'ChaCha20Poly1305Encryptor', 'AesGcmEncryptor']

class IEncryptor(metaclass=ABCMeta):
    'Static functions for encryption.'
    def __init__(self) -> None:
        'Encryptors cannot be instantiated.'
        raise Error('encryptors cannot be instantiated')
    @staticmethod
    @abstractmethod
    def encrypt(key: SymmetricKey, data: bytes) -> bytes:
        'Encrypts binary data with specific key.'
    @staticmethod
    @abstractmethod
    def decrypt(data: Ciphertext) -> bytes:
        'Decrypts specific ciphertext.'

class ChaCha20Poly1305Encryptor(IEncryptor):
    'Static functions for ChaCha20-Poly1305 encryption.'
    @staticmethod
    def encrypt(key: SymmetricKey, data: bytes) -> bytes:
        'Encrypts binary data with specific key.'
        cipher = aead.ChaCha20Poly1305(key.secret)
        nonce = os.urandom(12)
        ciphertext = cipher.encrypt(nonce, data, None)
        return key.withCiphertext(nonce + ciphertext)
    @staticmethod
    def decrypt(data: Ciphertext) -> bytes:
        'Decrypts specific ciphertext.'
        cipher = aead.ChaCha20Poly1305(data.secret)
        nonce, ciphertext = data.ciphertext[:12], data.ciphertext[12:]
        try:
            return cipher.decrypt(nonce, ciphertext, None)
        except InvalidTag:
            raise errors.InvalidCiphertext

class AesGcmEncryptor(IEncryptor):
    'Static functions for AES-256-GCM encryption.'
    @staticmethod
    def encrypt(key: SymmetricKey, data: bytes) -> bytes:
        'Encrypts binary data with specific key.'
        cipher = aead.AESGCM(key.secret)
        nonce = os.urandom(12)
        ciphertext = cipher.encrypt(nonce, data, None)
        return key.withCiphertext(nonce + ciphertext)
    @staticmethod
    def decrypt(data: Ciphertext) -> bytes:
        'Decrypts specific ciphertext.'
        cipher = aead.AESGCM(data.secret)
        nonce, ciphertext = data.ciphertext[:12], data.ciphertext[12:]
        try:
            return cipher.decrypt(nonce, ciphertext, None)
        except InvalidTag:
            raise errors.InvalidCiphertext