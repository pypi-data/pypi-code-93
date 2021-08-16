# -*- coding: utf-8 -*-
# @Time : 2020-06-09 14:07
# @Author : xzr
# @File : encrypt.py
# @Software: PyCharm
# @Contact : xzregg@gmail.com
# @Desc :


import base64
from Crypto.Cipher import AES
import gzip

'''
采用AES对称加密算法
'''

#实现 base64+gzip+AES-ECB

# str不是16的倍数那就补足为16的倍数
def add_to_16(value):
    while len(value) % 16 != 0:
        value += '\0'
    return str.encode(value)  # 返回bytes


KEY = 'slakdma'
# 加密方法
def encrypt(text, key=KEY):
    # 初始化加密器
    aes = AES.new(add_to_16(key), AES.MODE_ECB)
    # 先进行aes加密
    encrypt_aes = aes.encrypt(add_to_16(text))
    # 用base64转成字符串形式
    encrypted_text = base64.encodebytes(encrypt_aes)  # 执行加密并转码返回bytes  # str(encoding=utf-8)
    # gzip压缩
    en_gzip = gzip.compress(encrypted_text)
    # base64编码
    en_base64 = base64.b64encode(en_gzip)
    return en_base64


# 解密方法
def decrypt(encrypt_text, key=KEY):
    # 秘钥

    # 密文
    # base64解码
    de_base64 = base64.b64decode(encrypt_text)
    # gzip解压
    de_gzip = gzip.decompress(de_base64)

    text = str(de_gzip, encoding="utf-8")
    # 初始化加密器
    aes = AES.new(add_to_16(key), AES.MODE_ECB)
    # 优先逆向解密base64成bytes
    base64_decrypted = base64.decodebytes(text.encode(encoding='utf-8'))
    # 执行解密密并转码返回str
    decrypted_text = str(aes.decrypt(base64_decrypted), encoding='utf-8').replace('\0', '')
    return decrypted_text


if __name__ == '__main__':
    en_result = encrypt('alsdewtwet3q3eraqwrqwewewklasd')
    print(en_result)
    de_result = decrypt(en_result)
    print(de_result)