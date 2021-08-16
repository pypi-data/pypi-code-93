"""
使用标准的 AES/CBC/PKCS5PADDING  PBKDF2WithHmacSHA256  来加解密字符串
@author sun
@Date 2019-11-30 11:27
@version 1.0
"""

import base64
import hashlib

from Crypto import Random
from Crypto.Cipher import AES

block_size = 16
pad = lambda s: s + (block_size - len(s) % block_size) * chr(block_size - len(s) % block_size)
unpad = lambda s: s[0:-ord(s[-1:])]
iv = Random.new().read(AES.block_size) # Random IV

def __get_private_key(secret_key, salt):
    return hashlib.pbkdf2_hmac('SHA256', secret_key.encode(), salt.encode(), 65536, 32)

def encrypt_with_AES(message, secret_key, salt):
    """
    AES加密
    :param message: 明文. 只能是英文数字符号
    :param secret_key:
    :param salt:
    :return:
    """
    private_key = __get_private_key(secret_key, salt)
    message = pad(message)
    cipher = AES.new(private_key, AES.MODE_CBC, iv)
    cipher_bytes = base64.b64encode(iv + cipher.encrypt(message))
    return bytes.decode(cipher_bytes)

def decrypt_with_AES(encoded, secret_key, salt):
    """
    AES解密
    :param encoded:
    :param secret_key:
    :param salt:
    :return:
    """
    private_key = __get_private_key(secret_key, salt)
    cipher_text = base64.b64decode(encoded)
    iv = cipher_text[:AES.block_size]
    cipher = AES.new(private_key, AES.MODE_CBC, iv)
    plain_bytes = unpad(cipher.decrypt(cipher_text[block_size:]))
    return bytes.decode(plain_bytes)


if __name__ == '__main__':
    # 加解密测试

    secret_key = "$0bEyHive&2o1Six"
    salt = "JXTYp9icQaTzs4"
    plain_text = "English@12_d:a&^%*"

    cipher = encrypt_with_AES(plain_text, secret_key, salt)
    print("Cipher: " + cipher)

    decrypted = decrypt_with_AES(cipher, secret_key, salt)
    print("Decrypted " + decrypted)