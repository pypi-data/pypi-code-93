'''
psypher.secret - Module for psypher's asymmetric keys and key pairs.
'''

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric import ec, ed25519, x25519
from cryptography.hazmat.primitives.kdf import hkdf, pbkdf2
from cryptography.hazmat.primitives import keywrap, hashes, serialization, hmac
from abc import ABCMeta, abstractmethod
from . import errors, cache
import json, os

__all__ = ['SymmetricKey', 'Ciphertext', 'IPrivateKey',
    'IPublicKey', 'IKeyPair', 'Curve25519PrivateKey', 'Curve25519PublicKey',
    'EccPrivateKey', 'EccPublicKey', 'Curve25519KeyPair', 'EccKeyPair']

class SymmetricKey:
    'Represents a ephemeral key used in symmetric encryption.'
    def __init__(self, secret: bytes, ephemeral_public: bytes, salt: bytes) -> None:
        'Initializes with shared secret, ephemeral key and salt.'
        self.secret = secret
        self.ephemeral = ephemeral_public
        self.salt = salt
    def withCiphertext(self, ciphertext: bytes) -> None:
        'Concatenates the ciphertext.'
        return self.ephemeral + self.salt + ciphertext

class Ciphertext:
    'Represents a deconstructed ciphertext with secret.'
    def __init__(self, secret: bytes, ciphertext: bytes) -> None:
        'Initializes with symmetric key and ciphertext.'
        self.secret = secret
        self.ciphertext = ciphertext

class IPrivateKey(metaclass=ABCMeta):
    'Interface for general private keys.'
    @staticmethod
    @abstractmethod
    def generate() -> 'IPrivateKey':
        'Constructs a private key from generated keys.'
    @abstractmethod
    def export(self) -> bytes:
        'Exports this key as binary format.'
    @abstractmethod
    def exportJson(self) -> str:
        'Exports this key as JSON format.'
    @abstractmethod
    def secureExport(self, password: bytes, derive: bool = True) -> bytes:
        'Encrypts and exports this key as binary format.'
    @abstractmethod
    def secureExportJson(self, password: bytes, derive: bool = True) -> str:
        'Encrypts and exports this key as JSON format.'
    @staticmethod
    @abstractmethod
    def importKey(data: bytes) -> 'IPrivateKey':
        'Imports key from binary format.'
    @staticmethod
    @abstractmethod
    def importJson(data: str) -> 'IPrivateKey':
        'Imports key from JSON format.'
    @staticmethod
    @abstractmethod
    def secureImport(data: bytes, password: bytes, derive: bool=True) -> 'IPrivateKey':
        'Decrypts and imports key from binary format.'
    @staticmethod
    @abstractmethod
    def secureImportJson(data: str, password: bytes, derive: bool=True) -> 'IPrivateKey':
        'Decrypts and imports key from JSON format.'
    @property
    @abstractmethod
    def publicKey(self) -> 'IPublicKey':
        'Gets the corresponding public key.'

class IPublicKey(metaclass=ABCMeta):
    'Interface for general public keys.'
    @abstractmethod
    def export(self) -> bytes:
        'Exports this key as binary format.'
    @abstractmethod
    def exportJson(self) -> str:
        'Exports this key as JSON format.'
    @staticmethod
    @abstractmethod
    def importKey(data: bytes) -> 'IPublicKey':
        'Imports key from binary format.'
    @staticmethod
    @abstractmethod
    def importJson(data: str) -> 'IPublicKey':
        'Imports key from JSON format.'
    @property
    @cache.Cached
    def digest(self) -> bytes:
        'Calculates the hash digest of this key.'
        hasher = hashes.Hash(hashes.SHA256())
        hasher.update(self.export())
        return hasher.finalize()

class IKeyPair(metaclass=ABCMeta):
    'Represents a key pair to store desired keys.'
    @staticmethod
    @abstractmethod
    def generate() -> 'IKeyPair':
        'Generates a pair of keys.'
    @property
    @abstractmethod
    def privateKey(self) -> IPrivateKey:
        'Gets the private component of this pair.'
    @property
    @abstractmethod
    def publicKey(self) -> IPublicKey:
        'Gets the public component of this pair.'
    @property
    @abstractmethod
    def remoteKey(self) -> IPublicKey:
        'Gets the remote component of this pair.'
    @abstractmethod
    def setRemoteKey(self, key: IPublicKey) -> None:
        'Sets the remote component of this pair.'
    def export(self) -> bytes:
        'Shortcut for `publicKey.export`.'
        return self.publicKey.export()
    def exportJson(self) -> bytes:
        'Shortcut for `publicKey.exportJson`.'
        return self.publicKey.exportJson()
    @abstractmethod
    def receive(self, data: bytes) -> None:
        'Receives remote component from binary format.'
    @abstractmethod
    def receiveJson(self, data: str) -> None:
        'Receives remote component from JSON format.'
    @property
    @abstractmethod
    def sharedSecret(self) -> bytes:
        'Gets the negotiated shared secret.'
    @abstractmethod
    def getEphemeralKey(self) -> SymmetricKey:
        'Generates an ephemeral key for encryption.'
    @abstractmethod
    def parseCiphertext(self, data: bytes) -> Ciphertext:
        'Parses a ciphertext, extracting a symmetric key.'
    @abstractmethod
    def sign(self, data: bytes) -> bytes:
        'Signs the data with local private key.'
    @abstractmethod
    def verify(self, data: bytes, signature: bytes) -> bytes:
        'Verifies the data with remote public key.'

class Curve25519PrivateKey(IPrivateKey):
    'Represents a curve25519 private key which both sides keep for themselves.'
    def __init__(self,
        x25519_key: x25519.X25519PrivateKey,
        ed25519_key: ed25519.Ed25519PrivateKey) -> None:
        'Initializes a new instance from two keys. For internal use only.'
        self._x25519 = x25519_key
        self._ed25519 = ed25519_key
    @staticmethod
    def generate() -> 'Curve25519PrivateKey':
        'Constructs a new instance using generated keys.'
        return Curve25519PrivateKey(
            x25519.X25519PrivateKey.generate(),
            ed25519.Ed25519PrivateKey.generate()
        )
    def export(self) -> bytes:
        'Exports this key as binary format.' 
        key1 = self._x25519.private_bytes(
            serialization.Encoding.Raw,
            serialization.PrivateFormat.Raw,
            serialization.NoEncryption()
        )
        key2 = self._ed25519.private_bytes(
            serialization.Encoding.Raw,
            serialization.PrivateFormat.Raw,
            serialization.NoEncryption()
        )
        return key1 + key2
    def exportJson(self) -> str:
        'Exports this key as JSON format.'
        key1 = self._x25519.private_bytes(
            serialization.Encoding.Raw,
            serialization.PrivateFormat.Raw,
            serialization.NoEncryption()
        )
        key2 = self._ed25519.private_bytes(
            serialization.Encoding.Raw,
            serialization.PrivateFormat.Raw,
            serialization.NoEncryption()
        )
        return json.dumps({
            'x25519': key1.hex(),
            'ed25519': key2.hex()
        })
    def secureExport(self, password: bytes, derive: bool=True) -> bytes:
        'Encrypts and exports this key as binary format.'
        if derive:
            salt = os.urandom(16)
            password = pbkdf2.PBKDF2HMAC(hashes.SHA512(), 16, salt, 1000)
        else: salt = b''
        key1 = self._x25519.private_bytes(
            serialization.Encoding.Raw,
            serialization.PrivateFormat.Raw,
            serialization.NoEncryption()
        )
        key2 = self._ed25519.private_bytes(
            serialization.Encoding.Raw,
            serialization.PrivateFormat.Raw,
            serialization.NoEncryption()
        )
        return salt + keywrap.aes_key_wrap(password, key1) + keywrap.aes_key_wrap(password, key2)
    def secureExportJson(self, password: bytes, derive: bool=True) -> str:
        'Encrypts and exports this key as JSON format.'
        if derive:
            salt = os.urandom(16)
            password = pbkdf2.PBKDF2HMAC(hashes.SHA512(), 16, salt, 1000).derive(password)
        else: salt = b''
        key1 = self._x25519.private_bytes(
            serialization.Encoding.Raw,
            serialization.PrivateFormat.Raw,
            serialization.NoEncryption()
        )
        key2 = self._ed25519.private_bytes(
            serialization.Encoding.Raw,
            serialization.PrivateFormat.Raw,
            serialization.NoEncryption()
        )
        return json.dumps({
            'salt': salt.hex(),
            'x25519': keywrap.aes_key_wrap(password, key1).hex(),
            'ed25519': keywrap.aes_key_wrap(password, key2).hex()
        })
    @staticmethod
    def importKey(data: bytes) -> 'Curve25519PrivateKey':
        'Imports key from binary format.'
        try:
            key1 = data[:32]
            key2 = data[32:]
            return Curve25519PrivateKey(
                x25519.X25519PrivateKey.from_private_bytes(key1),
                ed25519.Ed25519PrivateKey.from_private_bytes(key2)
            )
        except ValueError:
            raise errors.InvalidKeyData('data must be 64 bytes long')
    @staticmethod
    def importJson(data: str) -> 'Curve25519PrivateKey':
        'Imports key from JSON format.'
        try:
            keys = json.loads(data)
            key1 = bytes.fromhex(keys['x25519'])
            key2 = bytes.fromhex(keys['ed25519'])
            return Curve25519PrivateKey(
                x25519.X25519PrivateKey.from_private_bytes(key1),
                ed25519.Ed25519PrivateKey.from_private_bytes(key2)
            )
        except (KeyError, ValueError, json.JSONDecodeError):
            raise errors.InvalidKeyData('json data is invalid')
    @staticmethod
    def secureImport(data: bytes, password: bytes, derive: bool=True) -> 'Curve25519PrivateKey':
        'Decrypts and imports key from binary format.'
        try:
            if derive:
                salt, data = data[:16], data[16:]
                password = pbkdf2.PBKDF2HMAC(hashes.SHA512(), 16, salt, 1000).derive(password)
            key1 = data[:32]
            key2 = data[32:]
            return Curve25519PrivateKey(
                x25519.X25519PrivateKey.from_private_bytes(keywrap.aes_key_unwrap(password, key1)),
                ed25519.Ed25519PrivateKey.from_private_bytes(keywrap.aes_key_unwrap(password, key2))
            )
        except ValueError:
            raise errors.InvalidKeyData('data must be 80 bytes long')
    @staticmethod
    def secureImportJson(data: str, password: bytes, derive: bool=True) -> 'Curve25519PrivateKey':
        'Decrypts and imports key from JSON format.'
        try:
            keys = json.loads(data)
            salt = bytes.fromhex(keys['salt'])
            key1 = bytes.fromhex(keys['x25519'])
            key2 = bytes.fromhex(keys['ed25519'])
            if derive:
                password = pbkdf2.PBKDF2HMAC(hashes.SHA512(), 16, salt, 1000).derive(password)
            return Curve25519PrivateKey(
                x25519.X25519PrivateKey.from_private_bytes(keywrap.aes_key_unwrap(password, key1)),
                ed25519.Ed25519PrivateKey.from_private_bytes(keywrap.aes_key_unwrap(password, key2))
            )
        except (ValueError, KeyError, json.JSONDecodeError):
            raise errors.InvalidKeyData('json data is invalid')
    @property
    def publicKey(self) -> 'Curve25519PublicKey':
        'Gets the corresponding public key.'
        return Curve25519PublicKey(self._x25519.public_key(), self._ed25519.public_key())

class Curve25519PublicKey(IPublicKey):
    'Represents a curve25519 public which both sides share with others.'
    def __init__(self,
        x25519_key: x25519.X25519PublicKey,
        ed25519_key: ed25519.Ed25519PublicKey) -> None:
        'Initializes a new instance from two keys. For internal use only.'
        self._x25519 = x25519_key
        self._ed25519 = ed25519_key
    def export(self) -> bytes:
        'Exports this key as binary format.' 
        key1 = self._x25519.public_bytes(
            serialization.Encoding.Raw,
            serialization.PublicFormat.Raw,
        )
        key2 = self._ed25519.public_bytes(
            serialization.Encoding.Raw,
            serialization.PublicFormat.Raw,
        )
        return key1 + key2
    def exportJson(self) -> str:
        'Exports this key as JSON format.'
        key1 = self._x25519.public_bytes(
            serialization.Encoding.Raw,
            serialization.PublicFormat.Raw,
        )
        key2 = self._ed25519.public_bytes(
            serialization.Encoding.Raw,
            serialization.PublicFormat.Raw,
        )
        return json.dumps({
            'x25519': key1.hex(),
            'ed25519': key2.hex()
        })
    @staticmethod
    def importKey(data: bytes) -> 'Curve25519PublicKey':
        'Imports key from binary format.'
        try:
            key1 = data[:32]
            key2 = data[32:]
            return Curve25519PublicKey(
                x25519.X25519PublicKey.from_public_bytes(key1),
                ed25519.Ed25519PublicKey.from_public_bytes(key2)
            )
        except ValueError:
            raise errors.InvalidKeyData('data must be 64 bytes long')
    @staticmethod
    def importJson(data: str) -> 'Curve25519PublicKey':
        'Imports key from JSON format.'
        try:
            keys = json.loads(data)
            key1 = bytes.fromhex(keys['x25519'])
            key2 = bytes.fromhex(keys['ed25519'])
            return Curve25519PublicKey(
                x25519.X25519PublicKey.from_public_bytes(key1),
                ed25519.Ed25519PublicKey.from_public_bytes(key2)
            )
        except (KeyError, ValueError, json.JSONDecodeError):
            raise errors.InvalidKeyData('json data is invalid')

class EccPrivateKey(IPrivateKey):
    'Represents an elliptic-curve private key which both sides keep for themselves.'
    def __init__(self, key: ec.EllipticCurvePrivateKeyWithSerialization) -> None:
        'Initializes with internal key. For internal use only.'
        self._key = key
    @staticmethod
    def generate() -> 'EccPrivateKey':
        'Constructs a private key from generated keys.'
        return EccPrivateKey(ec.generate_private_key(ec.SECP256K1()))
    def export(self) -> bytes:
        'Exports this key as binary format.'
        raise errors.UnexportableKey('EC private key cannot be exported. Use encode.Encoder instead.')
    def exportJson(self) -> str:
        'Exports this key as JSON format.'
        raise errors.UnexportableKey('EC private key cannot be exported. Use encode.Encoder instead.')
    def secureExport(self, password: bytes, derive: bool=True) -> bytes:
        'Encrypts and exports the key as binary format.'
        raise errors.UnexportableKey('EC private key cannot be exported. Use encode.Encoder instead.')
    def secureExportJson(self, password: bytes, derive: bool) -> str:
        'Encrypts and exports the key as JSON format.'
        raise errors.UnexportableKey('EC private key cannot be exported. Use encode.Encoder instead.')
    @staticmethod
    def importKey(data: bytes) -> 'EccPrivateKey':
        'Imports a key from binary format.'
        raise errors.UnexportableKey('EC private key cannot be imported. Use encode.Decoder instead.')
    @staticmethod
    def importJson(data: str) -> 'EccPrivateKey':
        'Imports a key from JSON format.'
        raise errors.UnexportableKey('EC private key cannot be imported. Use encode.Decoder instead.')
    @staticmethod
    def secureImport(data: bytes, password: bytes, derive: bool=True) -> 'EccPrivateKey':
        'Decrypts and imports a key from binary format.'
        raise errors.UnexportableKey('EC private key cannot be imported. Use encode.Decoder instead.')
    @staticmethod
    def secureImportJson(data: str, password: bytes, derive: bool=True) -> 'EccPrivateKey':
        'Decrypts and imports a key from JSON format.'
        raise errors.UnexportableKey('EC private key cannot be imported. Use encode.Decoder instead.')
    @property
    def publicKey(self) -> 'EccPublicKey':
        return EccPublicKey(self._key.public_key())

class EccPublicKey(IPublicKey):
    'Represents an elliptic-curve public key which both sides share with others.'
    def __init__(self, key: ec.EllipticCurvePublicKeyWithSerialization) -> None:
        'Initializes with internal key. For internal use only.'
        self._key = key
    def export(self) -> bytes:
        'Exports this key as binary format.'
        return self._key.public_bytes(
            serialization.Encoding.X962,
            serialization.PublicFormat.UncompressedPoint
        )
    def exportJson(self) -> str:
        'Exports this key as JSON format.'
        return json.dumps({
            'key': self._key.public_bytes(
                serialization.Encoding.X962,
                serialization.PublicFormat.UncompressedPoint
            ).hex()
        })
    @staticmethod
    def importKey(data: bytes) -> 'EccPublicKey':
        'Imports a key from binary format.'
        try:
            return EccPublicKey(ec.EllipticCurvePublicKeyWithSerialization.from_encoded_point(
                ec.SECP256K1(), data
            ))
        except ValueError:
            raise errors.InvalidKeyData('data must be 65 bytes long')
    @staticmethod
    def importJson(data: str) -> 'EccPublicKey':
        'Imports a key from JSON format.'
        try:
            keys = json.loads(data)
            return EccPublicKey(ec.EllipticCurvePublicKeyWithSerialization.from_encoded_point(
                ec.SECP256K1(), bytes.fromhex(keys['key'])
            ))
        except (ValueError, KeyError, json.JSONDecodeError):
            raise errors.InvalidKeyData('json data is invalid')

class Curve25519KeyPair(IKeyPair):
    'Represents a pair of curve25519 keys.'
    def __init__(self, private_key: Curve25519PrivateKey) -> None:
        'Initializes with private key.'
        self._private = private_key
        self._public = private_key.publicKey
        self._remote = None
    def _check(self, message: str='') -> None:
        'Checks the presence of the remote key.'
        if not self._remote:
            return errors.MissingRemoteKey(message)
    @staticmethod
    def generate() -> 'Curve25519KeyPair':
        'Generates a pair of keys.'
        return Curve25519KeyPair(Curve25519PrivateKey.generate())
    def receive(self, data: bytes) -> None:
        'Receives remote component from binary format.'
        self.setRemoteKey(Curve25519PublicKey.importKey(data))
    def receiveJson(self, data: str) -> None:
        'Receives remote component from JSON format.'
        self.setRemoteKey(Curve25519PublicKey.importJson(data))
    def setRemoteKey(self, key: Curve25519PublicKey) -> None:
        'Sets the remote component of this pair.'
        if self._remote and Curve25519KeyPair.sharedSecret.fget.enabled:
            raise errors.ForbiddenInCacheMode('when cache is enabled, you cannot set remote key twice')
        self._remote = key
    @property
    def privateKey(self) -> Curve25519PrivateKey:
        'The private component of this pair.'
        return self._private
    @property
    def publicKey(self) -> Curve25519PublicKey:
        'The public component of this pair.'
        return self._public
    @property
    def remoteKey(self) -> Curve25519PublicKey:
        'The remote component of this pair.'
        self._check('remote key not received yet')
        return self._remote
    @property
    @cache.Cached
    def sharedSecret(self) -> bytes:
        'Gets the negotiated shared secret.'
        self._check('remote key must be present to calculate shared secret')
        secret = self._private._x25519.exchange(self._remote._x25519)
        kdf = hkdf.HKDFExpand(hashes.SHA512(), 32, None)
        return kdf.derive(secret)
    def getEphemeralKey(self) -> SymmetricKey:
        'Generates an ephemeral key for encryption.'
        self._check('remote key must be present to generate symmetric key')
        ephemeral = x25519.X25519PrivateKey.generate()
        secret = ephemeral.exchange(self._remote._x25519)
        salt = os.urandom(16)
        kdf = hkdf.HKDF(hashes.SHA512(), 32, salt, None)
        secret = kdf.derive(secret)
        return SymmetricKey(secret, ephemeral.public_key().public_bytes(
            serialization.Encoding.Raw,
            serialization.PublicFormat.Raw
        ), salt)
    def parseCiphertext(self, data: bytes) -> Ciphertext:
        'Parses a ciphertext, extracting a symmetric key.'
        ephemeral_bytes, salt, data = data[:32], data[32:48], data[48:]
        ephemeral = x25519.X25519PublicKey.from_public_bytes(ephemeral_bytes)
        secret = self._private._x25519.exchange(ephemeral)
        kdf = hkdf.HKDF(hashes.SHA512(), 32, salt, None)
        secret = kdf.derive(secret)
        return Ciphertext(secret, data)
    def sign(self, data: bytes) -> bytes:
        'Signs the data with local private key.'
        hasher = hashes.Hash(hashes.SHA384())
        hasher.update(data)
        return self._private._ed25519.sign(hasher.finalize())
    def verify(self, data: bytes, signature: bytes) -> bool:
        'Verifies the data with remote public key.'
        self._check('remote key must be present to verify signature')
        hasher = hashes.Hash(hashes.SHA384())
        hasher.update(data)
        try:
            self._remote._ed25519.verify(signature, hasher.finalize())
            return True
        except InvalidSignature:
            return False

class EccKeyPair(IKeyPair):
    'Represents a pair of ECC keys.'
    def __init__(self, private_key: EccPrivateKey) -> None:
        'Initializes with private key.'
        self._private = private_key
        self._public = private_key.publicKey
        self._remote = None
    def _check(self, message: str='') -> None:
        'Checks the presence of the remote key.'
        if not self._remote:
            return errors.MissingRemoteKey(message)
    @staticmethod
    def generate() -> 'EccKeyPair':
        'Generates a pair of keys.'
        return EccKeyPair(EccPrivateKey.generate())
    def receive(self, data: bytes) -> None:
        'Receives remote component from binary format.'
        self.setRemoteKey(EccPublicKey.importKey(data))
    def receiveJson(self, data: str) -> None:
        'Receives remote component from JSON format.'
        self.setRemoteKey(EccPublicKey.importJson(data))
    def setRemoteKey(self, key: EccPublicKey) -> None:
        'Sets the remote component of this pair.'
        if self._remote and EccKeyPair.sharedSecret.fget.enabled:
            raise errors.ForbiddenInCacheMode('when cache is enabled, you cannot set remote key twice')
        self._remote = key
    @property
    def privateKey(self) -> EccPrivateKey:
        'The private component of this pair.'
        return self._private
    @property
    def publicKey(self) -> EccPublicKey:
        'The public component of this pair.'
        return self._public
    @property
    def remoteKey(self) -> EccPublicKey:
        'The remote component of this pair.'
        self._check('remote key not received yet')
        return self._remote
    @property
    @cache.Cached
    def sharedSecret(self) -> bytes:
        'Gets the negotiated shared secret.'
        self._check('remote key must be present to calculate shared secret')
        secret = self._private._key.exchange(ec.ECDH(), self._remote._key)
        kdf = hkdf.HKDFExpand(hashes.SHA512(), 32, None)
        return kdf.derive(secret)
    def getEphemeralKey(self) -> SymmetricKey:
        'Generates an ephemeral key for encryption.'
        self._check('remote key must be present to generate symmetric key')
        ephemeral = ec.generate_private_key(ec.SECP256K1())
        secret = ephemeral.exchange(ec.ECDH(), self._remote._key)
        salt = os.urandom(16)
        kdf = hkdf.HKDF(hashes.SHA512(), 32, salt, None)
        secret = kdf.derive(secret)
        return SymmetricKey(secret, ephemeral.public_key().public_bytes(
            serialization.Encoding.X962,
            serialization.PublicFormat.UncompressedPoint
        ), salt)
    def parseCiphertext(self, data: bytes) -> Ciphertext:
        'Parses a ciphertext, extracting a symmetric key.'
        ephemeral_bytes, salt, data = data[:65], data[65:81], data[81:]
        ephemeral = ec.EllipticCurvePublicKey.from_encoded_point(ephemeral_bytes)
        secret = self._private._key.exchange(ec.ECDH(), ephemeral)
        kdf = hkdf.HKDF(hashes.SHA512(), 32, salt, None)
        secret = kdf.derive(secret)
        return Ciphertext(secret, data)
    def sign(self, data: bytes) -> bytes:
        'Signs the data with local private key.'
        return self._private._key.sign(data, ec.ECDSA(hashes.SHA384()))
    def verify(self, data: bytes, signature: bytes) -> bool:
        'Verifies the data with remote public key.'
        self._check('remote key must be present to verify signature')
        try:
            self._remote._key.verify(signature, data, ec.ECDSA(hashes.SHA384()))
            return True
        except InvalidSignature:
            return False