#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Author: zhangkai
Last modified: 2020-06-14 19:33:33
'''
import binascii

import rsa
from Crypto.Cipher import AES, DES

from .base_utils import to_bytes, to_str


class Crypt:

    @staticmethod
    def _unpad(s):
        ''' 删除 PKCS#7 方式填充的字符串
        '''
        return s[:-ord(s[len(s) - 1:])]

    @staticmethod
    def _pad(text, size=8):
        length = len(text)
        val = size - (length % size)
        pad = f'{val:02x}' * val
        return text + binascii.unhexlify(pad)

    @classmethod
    def des_encrypt(cls, message, key):
        ''' key: 8位 '''
        message = cls._pad(to_bytes(message), DES.block_size)
        key = to_bytes(key)
        cipher = DES.new(to_bytes(key), DES.MODE_ECB)
        encrypt_data = cipher.encrypt(message)
        return to_str(binascii.b2a_hex(encrypt_data))

    @classmethod
    def des_decrypt(cls, ciphertext, key):
        data = binascii.a2b_hex(ciphertext)
        cipher = DES.new(to_bytes(key), DES.MODE_ECB)
        return to_str(cls._unpad(cipher.decrypt(data)))

    @classmethod
    def aes_encrypt(cls, message, key, iv=None):
        ''' key: 32位 '''
        message = cls._pad(to_bytes(message), AES.block_size)
        key = to_bytes(key)
        iv = iv or key[:16]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        encrypt_data = cipher.encrypt(message)
        return to_str(binascii.b2a_hex(encrypt_data))

    @classmethod
    def aes_decrypt(cls, ciphertext, key, iv=None):
        data = binascii.a2b_hex(ciphertext)
        key = to_bytes(key)
        iv = iv or key[:16]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        return to_str(cls._unpad(cipher.decrypt(data)))

    @ classmethod
    def gen_rsa_key(cls, length=1024):
        pubkey, privkey = rsa.newkeys(length)
        return pubkey.save_pkcs1(), privkey.save_pkcs1()

    @ classmethod
    def rsa_encrypt(cls, message, pubkey):
        if not isinstance(pubkey, rsa.PublicKey):
            pubkey = rsa.PublicKey.load_pkcs1(to_bytes(pubkey))
        encrypt_data = rsa.encrypt(to_bytes(message), pubkey)
        return to_str(binascii.b2a_hex(encrypt_data))

    @ classmethod
    def rsa_decrypt(cls, ciphertext, privkey):
        if not isinstance(privkey, rsa.PrivateKey):
            privkey = rsa.PrivateKey.load_pkcs1(to_bytes(privkey))
        data = binascii.a2b_hex(ciphertext)
        return to_str(rsa.decrypt(data, privkey))
