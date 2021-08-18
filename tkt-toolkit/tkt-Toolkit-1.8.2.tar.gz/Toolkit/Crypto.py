from cryptography.fernet import Fernet
import base64,os
cheddar = b's9ONoNb1dpPZvYyLGqrbdWiKhj547EXIHz6VWMBL8F8='
class bunny:
    def create_key(S=""):
        key__ = base64.urlsafe_b64encode(os.urandom(32))
        return key__
    def encrypt(key: bytes, plain: bytes):
        cipher_suite = Fernet(key)
        cipher_text = cipher_suite.encrypt(plain)
        return cipher_text
    def decrypt(key: bytes, cipher_text: bytes):
        cipher_suite = Fernet(key)
        plain_text = cipher_suite.decrypt(cipher_text)
        return plain_text
class crypto:
    def encrypt(text:bytes):
        """
        Uses xor to encrypt 'text', the key
        gets encrypted using basic cryptography
        with cheddar, to make it more user friendly and shorter.
        """
        size = len(text)
        key = os.urandom(size)
        l = bytes(a ^ b for (a, b) in zip(text, key))
        a_key = bunny.encrypt(cheddar,key)
        return (l,a_key)
    def decrypt(key:bytes,enc_text:bytes):
        """
        Uses basic cryptography and xor to decrypt 'enc_text'
        the key is encrypted using cryptography with cheddar
        and decrypts 'enc_text' using the xor key.
        """
        key_ = bunny.decrypt(cheddar,key)
        l = bytes(a ^ b for (a, b) in zip(enc_text, key_))
        return l