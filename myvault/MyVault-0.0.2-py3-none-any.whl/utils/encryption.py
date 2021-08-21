import base64
import hashlib

from Crypto import Random
from Crypto.Cipher import AES


class AESEncryption:
    def __init__(self, key: str, salt: str, iterations: int):
        self.key = self.__get_sha256(text=key, salt=salt, iterations=iterations)

    @staticmethod
    def __get_sha256(text: str, salt: str = "", iterations: int = 10000) -> bytes:
        return hashlib.pbkdf2_hmac(
            hash_name="sha256",
            password=text.encode(encoding="utf-8"),
            salt=salt.encode(),
            iterations=iterations,
        )

    def encrypt(self, plaintext: str) -> str:
        raw_padded = self.__get_padded_text(text=plaintext)
        init_vector = Random.new().read(AES.block_size)
        cipher = AES.new(key=self.key, mode=AES.MODE_CBC, iv=init_vector)
        encrypted_bytes = base64.b64encode(init_vector + cipher.encrypt(raw_padded.encode()))
        return encrypted_bytes.decode()

    @staticmethod
    def __get_padded_text(text: str) -> str:
        return text + (AES.block_size - len(text) % AES.block_size) * chr(AES.block_size - len(text) % AES.block_size)

    def decrypt(self, ciphertext: str) -> str:
        ciphertext_as_byte = base64.b64decode(ciphertext)
        init_vector = ciphertext_as_byte[: AES.block_size]
        cipher = AES.new(key=self.key, mode=AES.MODE_CBC, iv=init_vector)
        decrypted_bytes = self.__get_unpadded_bytes(cipher.decrypt(ciphertext_as_byte[AES.block_size :]))
        return decrypted_bytes.decode()

    @staticmethod
    def __get_unpadded_bytes(text: bytes) -> bytes:
        return text[: -ord(text[len(text) - 1 :])]
