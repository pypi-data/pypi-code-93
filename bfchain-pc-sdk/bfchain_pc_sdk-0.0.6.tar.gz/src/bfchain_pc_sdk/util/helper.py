# -*- coding: utf-8 -*-
import base64
import hashlib
import json
import requests
import base58
from number import hex_to_byte, byte_to_hex
from src.bfchain_pc_sdk.util.tweetnacl import (
    create_seed_from_string,
    nacl_sign_keypair_from_seed,
    nacl_sign_keypair_from_secret_key,
create_byte_list_from_byte_list_by_sha256,
nacl_sign_detached
)


def get_pk_sk_from_mnemonic_words(words):
    seed = create_seed_from_string(words)
    pk, sk = nacl_sign_keypair_from_seed(seed)
    pk2, sk2 = nacl_sign_keypair_from_secret_key(sk)
    return byte_to_hex(pk2), byte_to_hex(sk2)


def get_address(public_key, prefix):
    if isinstance(public_key,str):
        public_key = hex_to_byte(public_key, False)
    if not isinstance(public_key, list):
        raise TypeError("公钥参数应该为字节数组")
    public_key_sha256 = hex_to_byte(hashlib.sha256(bytearray(public_key)).hexdigest(), False)
    ripemd160 = hashlib.new('ripemd160')
    ripemd160.update(bytearray(public_key_sha256))
    buf = ripemd160.hexdigest()
    buf2 = hashlib.sha256(bytearray(hex_to_byte(buf, False))).hexdigest()
    buf2 = hashlib.sha256(bytearray(hex_to_byte(buf2, False))).hexdigest()
    buf_array = hex_to_byte(buf, False)
    buf2_array = hex_to_byte(buf2, False)
    result = []
    result.extend(buf_array)
    result.extend(buf2_array[:4])
    return str(prefix + base58.encode(result))


def signature_message(buf, sk):
    """

    :param buf: 字符串格式的创建事件信息体
    :param sk: 字符串格式的私钥
    :return: 字符串格式的信息签名
    """
    base64_buf = bytearray(base64.decodestring(buf))
    base64_buf_bytes = [0] *len(base64_buf)
    for i in range(len(base64_buf)):
        base64_buf_bytes[i] = base64_buf[i]
    msg = create_byte_list_from_byte_list_by_sha256(base64_buf_bytes)
    rnt = nacl_sign_detached(msg,hex_to_byte(sk,False))
    return base64_buf_bytes,byte_to_hex(rnt)


def get(url, data):
    res = requests.get(url, params=data).json()
    if res['success']:
        return res['result']
    else:
        raise RuntimeError(str(res['error']['message']))


def post(url, data):
    headers = {'content-type': 'application/json'}
    res = requests.post(url, data=json.dumps(data), headers=headers).json()
    if res['success']:
        return res['result']
    else:
        raise RuntimeError(str(res['error']['message']))
