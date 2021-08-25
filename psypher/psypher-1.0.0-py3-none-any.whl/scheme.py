'''
psypher.scheme - Automated and modern key establishment, signature and encryption schemes.
'''

from typing import Type
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, hmac
from .cipher import *
from .errors import InvalidCiphertext
from .secret import Curve25519KeyPair, EccKeyPair, IKeyPair, IPublicKey

__all__ = ['Scheme', 'Curve25519ChaCha20Poly1305Scheme', 'Secp256k1AesGcmScheme']

class Scheme:
    'Represents an automated scheme with key agreement, integrity check, signature and encryption.'
    def __init__(self, pair: IKeyPair, encryptor: Type[IEncryptor]) -> None:
        'Initializes with key pair and encryptor class.'
        self._pair = pair
        self._encryptor = encryptor
    @property
    def keyPair(self) -> IKeyPair:
        'Gets the key pair referenced by this instance.'
        return self._pair
    @property
    def encryptor(self) -> Type[IEncryptor]:
        'Gets the encryptor class references by this instance.'
        return self._encryptor
    def sign(self, data: bytes) -> bytes:
        'Shortcut for `keyPair.sign`.'
        return self._pair.sign(data)
    def verify(self, data: bytes, signature: bytes) -> bool:
        'Shortcut for `keyPair.verify`.'
        return self._pair.verify(data, signature)
    def export(self) -> bytes:
        'Shortcut for `keyPair.export`.'
        return self._pair.export()
    def exportJson(self) -> str:
        'Shortcut for `keyPair.exportJson`.'
        return self._pair.exportJson()
    def receive(self, data: bytes) -> None:
        'Shortcut for `keyPair.receive`.'
        self._pair.receive(data)
    def receiveJson(self, data: str) -> None:
        'Shortcut for `keyPair.receiveJson`.'
        self._pair.receiveJson(data)
    def setRemoteKey(self, key: IPublicKey) -> None:
        'Shortcut for `keyPair.setRemoteKey`.'
        self._pair.setRemoteKey(key)
    @property
    def sharedSecret(self) -> bytes:
        'Shortcut for `keyPair.sharedSecret`.'
        return self._pair.sharedSecret
    def encrypt(self, data: bytes) -> bytes:
        'Encrypts the data with remote public key.'
        key = self._pair.getEphemeralKey()
        return self._encryptor.encrypt(key, data)
    def decrypt(self, data: bytes) -> bytes:
        'Decrypts the data with local private key.'
        try:
            ciphertext = self._pair.parseCiphertext(data)
        except ValueError:
            raise InvalidCiphertext
        return self._encryptor.decrypt(ciphertext)
    def integritySign(self, data: bytes) -> bytes:
        'Generates the MAC of the given message.'
        mac = hmac.HMAC(self._pair.sharedSecret, hashes.SHA256())
        mac.update(data)
        return mac.finalize()
    def integrityVerify(self, data: bytes, mactag: bytes) -> bool:
        'Verifies the MAC of the given message.'
        mac = hmac.HMAC(self._pair.sharedSecret, hashes.SHA256())
        mac.update(data)
        try:
            mac.verify(mactag)
            return True
        except InvalidSignature:
            return False
    @staticmethod
    def default() -> 'Curve25519ChaCha20Poly1305Scheme':
        'Constructs the default scheme using generated keys.'
        return Curve25519ChaCha20Poly1305Scheme.generate()

class Curve25519ChaCha20Poly1305Scheme(Scheme):
    'Represents a scheme using curve25519 keys and ChaCha20-Poly1305 encryption.'
    @staticmethod
    def generate() -> 'Curve25519ChaCha20Poly1305Scheme':
        'Constructs this scheme using generated keys.'
        return Curve25519ChaCha20Poly1305Scheme(Curve25519KeyPair.generate())
    def __init__(self, pair: Curve25519KeyPair) -> None:
        'Initializes with curve25519 key pair.'
        super().__init__(pair, ChaCha20Poly1305Encryptor)

class Secp256k1AesGcmScheme(Scheme):
    'Represents a scheme using secp256k1 keys and AES-256-GCM encryption.'
    @staticmethod
    def generate() -> 'Secp256k1AesGcmScheme':
        'Constructs this scheme using generated keys.'
        return Secp256k1AesGcmScheme(EccKeyPair.generate())
    def __init__(self, pair: EccKeyPair) -> None:
        'Initializes with elliptic-curve key pair.'
        super().__init__(pair, AesGcmEncryptor)