
# -*- coding: utf-8 -*-

# ===================================================================
# The contents of this file are dedicated to the public domain.  To
# the extent that dedication to the public domain is not available,
# everyone is granted a worldwide, perpetual, royalty-free,
# non-exclusive license to exercise all rights associated with the
# contents of this file for any purpose whatsoever.
# KaisaGlobal rights are reserved.
# ===================================================================

"""
This code provide basic encryption function for KaisaGlobal-Open.

developed by KaisaGlobal quant team.
2020.12.11
"""

import json, sys
from os.path import dirname, abspath
project_path = dirname(dirname(abspath(__file__)))
projec_full_path = project_path + r'\common'
sys.path.append(projec_full_path)

import requests
import base64
import random
from urllib import parse

from KCrypto.Cipher import PKCS1_v1_5
from KCrypto.Hash import SHA
from KCrypto.PublicKey import RSA
from KCrypto.Cipher import AES
from hashlib import md5


class KaisaCrypto(object):

    def __init__(self):

        self.aes_secret_key_secret = ""

    def encrypt_aes_password(self, text, type="MARKET", AES_SECRET_KEY=None):

        IV = "kai&sa!global@)!"
        if AES_SECRET_KEY is None:
            if type=="TRADE":
                AES_SECRET_KEY = 'login&pwd@glob)!'
            elif type=="MARKET":
                AES_SECRET_KEY = "third&log@glob)!"
            elif type=="SECRET":
                AES_SECRET_KEY = self.aes_secret_key_secret
            else:
                AES_SECRET_KEY = "third&log@glob)!"
        # padding algo.
        BS = len(AES_SECRET_KEY)
        pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
        unpad = lambda s: s[0:-ord(s[-1:])]
        cryptor = AES.new(AES_SECRET_KEY.encode("utf8"), AES.MODE_CBC, IV.encode("utf8"))
        ciphertext = cryptor.encrypt(bytes(pad(text), encoding="utf8"))
        encrypt_password = base64.b64encode(ciphertext)
        password = parse.quote(encrypt_password, "\\")
        return password

    def encrypt_aes_password_forQ(self, text, type="MARKET", AES_SECRET_KEY=None):

        IV = "kai&sa!global@)!"
        if AES_SECRET_KEY is None:
            if type == "TRADE":
                AES_SECRET_KEY = 'login&pwd@glob)!'
            elif type == "MARKET":
                AES_SECRET_KEY = "third&log@glob)!"
            elif type == "SECRET":
                AES_SECRET_KEY = self.aes_secret_key_secret
            else:
                AES_SECRET_KEY = "third&log@glob)!"
        # padding algo.
        BS = len(AES_SECRET_KEY)
        PADDING = '\n'
        pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
        cryptor = AES.new(AES_SECRET_KEY.encode("utf8"), AES.MODE_CBC, IV.encode("utf8"))
        ciphertext = cryptor.encrypt(bytes(pad(text), encoding="utf8"))
        encrypt_password = base64.b64encode(ciphertext)
        encrypt_password = encrypt_password.decode("utf8")
        return encrypt_password

    def decrypt_aes_password(self, encrypted, AES_SECRET_KEY):

        # encrypt_password
        IV = "kai&sa!global@)!"
        decrypted = base64.b64decode(encrypted)
        cryptor = AES.new(AES_SECRET_KEY.encode("utf8"), AES.MODE_CBC, IV.encode("utf8"))
        decrypted = cryptor.decrypt(decrypted)
        unpad = lambda s: s[0:-ord(s[-1:])]
        decrypted = unpad(decrypted)
        return decrypted

    def encrypt_rsa_username(self, username, crypto_rsa_url):

        account_rsa = requests.get(url=crypto_rsa_url, params={'username': username})
        if (account_rsa.status_code // 100!=2):
            return None
        pubkey = json.loads(account_rsa.text)["body"]
        pubkey_lines = []
        for i in range(len(pubkey)//64 + 1):
            str_ = pubkey[i * 64:(i+1) * 64]
            if len(str_) > 0:
                pubkey_lines.append(str_)
        pubkey_lines = ["-----BEGIN RSA PUBLIC KEY-----"] + pubkey_lines + ["-----END RSA PUBLIC KEY-----"]
        pubkey = "\n".join(pubkey_lines)

        cipher_public = PKCS1_v1_5.new(RSA.importKey(pubkey.encode()))
        cipher_text = base64.b64encode(cipher_public.encrypt(username.encode()))
        username_rsa = cipher_text.decode()
        return username_rsa


    def encrypt_rsa_secretQ(self, crypto_rsa_url):

        private_text = self._produce_encrypt_privatekey()
        account_rsa = requests.get(url=crypto_rsa_url)
        if (account_rsa.status_code//100!=2):
            return None
        pubkey = json.loads(account_rsa.text)["body"]
        pubkey_lines = []
        for i in range(len(pubkey)//64 +1):
            str_ = pubkey[(i) *64:( i+1 ) *64]
            if len(str_ ) >0:
                pubkey_lines.append(str_)
        pubkey_lines = ["-----BEGIN RSA PUBLIC KEY-----"] + pubkey_lines + ["-----END RSA PUBLIC KEY-----"]
        pubkey = "\n".join(pubkey_lines)
        cipher_public = PKCS1_v1_5.new(RSA.importKey(pubkey.encode()))
        cipher_text = base64.b64encode(cipher_public.encrypt(private_text.encode()))
        cipher_text_rsa = cipher_text.decode()
        return cipher_text_rsa

    def encrypt_md5(self, str_):
        obj_md5 = md5()
        obj_md5.update(str_.encode(encoding='utf-8'))
        return obj_md5.hexdigest()

    def _produce_encrypt_privatekey(self, length=16):

        H = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
        str_ = ""
        for i in range(length):
            str_+= random.choice(H)
        self.aes_secret_key_secret = str_
        return str_

    def get_encrypt_private(self):
        return self.private_key_trades

