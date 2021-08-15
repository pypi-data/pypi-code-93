import hashlib
from jsbn import RSAKey

class EncryptDecrypt:
    @staticmethod
    def enc_sha1(value:str):
        return hashlib.sha1(value.encode()).hexdigest()

    @staticmethod
    def enc_sha256(value:str):
        return hashlib.sha256(value.encode()).hexdigest()

    @staticmethod
    def rsa_enc(key,text):
        rsa = RSAKey()
        rsa.setPublic(key,"10001")

        return rsa.encrypt(text)