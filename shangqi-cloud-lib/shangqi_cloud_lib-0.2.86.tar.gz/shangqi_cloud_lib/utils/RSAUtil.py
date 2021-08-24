import base64

import rsa

from shangqi_cloud_lib.context import config


def newkeys(nbits=1024, **kwargs):
    return rsa.newkeys(nbits, **kwargs)


def base64keys(nbits=1024, **kwargs):
    public_key, private_key = rsa.newkeys(nbits, **kwargs)
    public_key_base64 = base64.encodebytes(public_key.save_pkcs1())
    private_key_base64 = base64.encodebytes(private_key.save_pkcs1())
    return public_key_base64, private_key_base64


def decrypt(content, private_key):
    if config.rsa:
        content = rsa.decrypt(content, private_key)
    return content


def encrypt(content, public_key):
    if config.rsa:
        content = rsa.encrypt(content, public_key)
    return content
