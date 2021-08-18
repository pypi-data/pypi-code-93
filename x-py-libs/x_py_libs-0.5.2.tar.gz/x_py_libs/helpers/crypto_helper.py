# -*- coding=utf-8 -*-

import json

from Crypto.Cipher import AES
from Crypto.Hash import MD5

from binascii import b2a_hex, a2b_hex, hexlify, unhexlify
from base64 import b64encode, b64decode

from x_py_libs.libs import PKCS7Encoder

# __KEY = '12345678900000001234567890000000'
# __IV = '1234567890000000'

# _KEY = bytearray(__KEY, 'utf8')
# _IV = bytearray(__IV, 'utf8')


__KEY = '12345678900000001234567890000000'
__IV = '1234567890000000'
_KEY = bytes(__KEY, 'utf8')
_IV = bytes(__IV, 'utf8')


class CryptoHelper(object):

    KEY = _KEY
    IV = _IV

    # @property
    # def __KEY(self):
    #     return '12345678900000001234567890000000'

    # @property
    # def __IV(self):
    #     return '1234567890000000'

    # @property
    # def _KEY(self):
    #     return bytes(self.__KEY, 'utf8')

    # @property
    # def _IV(self):
    #     return bytes(self.__IV, 'utf8')

    @staticmethod
    def encrypt_by_md5(plain_text):
        h = MD5.new()
        h.update(bytes(plain_text, 'utf8'))
        return h.hexdigest()

    @staticmethod
    def encrypt_by_aes(plain_text):

        # key = self._KEY

        # key_length = len(key)
        # if (key_length >= 32):
        #     k = key[:32]
        # elif (key_length >= 24):
        #     k = key[:24]
        # else:
        #     k = key[:16]

        # print len(text)
        if type(plain_text) is not str:
            plain_text = json.dumps(plain_text)

        cryptor = AES.new(_KEY, AES.MODE_CBC, _IV)
        pad_text = PKCS7Encoder.encode(plain_text)
        # ciphertext = cryptor.encrypt(bytearray(pad_text,'utf-8'))
        ciphertext = cryptor.encrypt(pad_text)
        # print(ciphertext)
        return str(b2a_hex(ciphertext), encoding='utf-8').upper()
        # return ciphertext

    @staticmethod
    def decrypt_by_aes(ciphertext):
        cryptor = AES.new(_KEY, AES.MODE_CBC, _IV)
        pad_text = cryptor.decrypt(a2b_hex(ciphertext))
        # return str(plain_text).rstrip('\x0c')
        try:
            return PKCS7Encoder.decode(pad_text).decode('utf-8')
        except:
            return None
