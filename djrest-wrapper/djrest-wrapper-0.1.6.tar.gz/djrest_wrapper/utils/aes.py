from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad
from base64 import b64encode, b64decode
from django.conf import settings


class AesCipher:

    def __init__(self, key: bytes = None, iv: bytes = None):
        try:
            self.key = b64decode(settings.AES_KEY)
            self.iv = b64decode(settings.AES_IV)
        except:
            self.key = key
            self.iv = iv

    def encrypt(self, data: str):
        cipher = AES.new(self.key, AES.MODE_CBC, iv=self.iv)
        ciphertext = cipher.encrypt(pad(data.encode(), AES.block_size))
        return b64encode(ciphertext).decode()

    def decrypt(self, ciphertext):
        cipher = AES.new(self.key, AES.MODE_CBC, iv=self.iv)
        plaintext = unpad(cipher.decrypt(
            b64decode(ciphertext)), AES.block_size)
        return plaintext.decode()
