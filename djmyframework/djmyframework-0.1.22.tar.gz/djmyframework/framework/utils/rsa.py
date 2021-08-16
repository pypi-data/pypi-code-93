# coding:utf-8

from Crypto import Signature
from Crypto.Cipher import PKCS1_v1_5 as PKCS1_v1_5_Cipher
from Crypto.Hash import SHA, MD5, SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Util import number
from Crypto.Util._number_new import ceil_div
from xml.dom.minidom import parseString
import M2Crypto
import Crypto
import base64
import binascii
import os
import re
from pyDes import *

private_key_tpl = '''-----BEGIN PRIVATE KEY-----
%s
-----END PRIVATE KEY-----
'''

public_key_tpl = '''-----BEGIN PUBLIC KEY-----
%s
-----END PUBLIC KEY-----'''

def ensure_utf8(s):
    if isinstance(s, str):
        return s.encode('utf8')
    return s


def decode_base64(data):
    """Decode base64, padding being optional.

    :param data: Base64 data as an ASCII byte string
    :returns: The decoded byte string.

    """
    missing_padding = 4 - len(data) % 4
    if missing_padding:
        data += b'=' * missing_padding
    return base64.decodestring(data)


def base64ToString(s):
    return decode_base64(s)
    return base64.decodestring(s)
    try:
        return base64.b64decode(s)
    except binascii.Error as e:
        raise SyntaxError(e)
    except binascii.Incomplete as e:
        raise SyntaxError(e)


def stringToBase64(s):
    return base64.encodestring(s).replace("\n", "")


def decrypt_with_rsa(msg, key):
    '''
    msg必须采用base64编码，　注意: base64编码的数据经过URLDecoder处理之后，可能不正确，其中的＋会变成' '
    '''
    msg = base64ToString(msg)
    key = RSA.importKey(key)
    cipher = PKCS1_v1_5_Cipher.new(key)

    modBits = number.size(key.n)
    k = ceil_div(modBits, 8)  # Convert from bits to bytes
    print("K: ", k)

    msglen = len(msg)
    msg_encryted = ""
    start_idx = 0
    # 处理过长的加密
    while msglen > 0:
        len1 = min([msglen, k])
        cleartext = cipher.decrypt(msg[start_idx: (start_idx + len1)], "")
        msg_encryted = msg_encryted + cleartext
        start_idx = start_idx + len1
        msglen = msglen - len1
    return msg_encryted


def encrypt_with_rsa(msg, key):
    '''
    msg必须采用utf8编码
    '''
    msg = ensure_utf8(msg)

    key = RSA.importKey(key)
    cipher = PKCS1_v1_5_Cipher.new(key)

    modBits = number.size(key.n)
    k = ceil_div(modBits, 8) - 28  # 11 # Convert from bits to bytes
    print("K: ", k)

    msglen = len(msg)
    msg_encryted = ""
    start_idx = 0
    # 处理过长的加密
    while msglen > 0:
        len1 = min([msglen, k])
        encrypt = cipher.encrypt(msg[start_idx: (start_idx + len1)])
        msg_encryted = msg_encryted + encrypt
        start_idx = start_idx + len1
        msglen = msglen - len1
    return stringToBase64(msg_encryted)


def check_with_rsa(msg, signature, key, method="SHA"):
    '''
    使用当前文件中定义的_public_rsa_key来验证签名是否正确
    '''
    signature = base64ToString(signature)
    key = RSA.importKey(key)
    if method == "SHA":
        h = SHA.new(msg)
    elif method == "SHA256":
        h = SHA256.new(msg)
    elif method == "MD5":
        h = MD5.new(msg)
    else:
        h = SHA.new(msg)
    verifier = PKCS1_v1_5.new(key)

    return verifier.verify(h, signature)


def sign_with_rsa(msg, key, method="SHA"):
    '''
    将msg使用当前文件中定义的_private_rsa_key来签名, 返回base64编码的字符串
    '''
    key = RSA.importKey(key)
    if method == "SHA":
        h = SHA.new(msg)
    elif method == "SHA256":
        h = SHA256.new(msg)
    elif method == "MD5":
        h = MD5.new(msg)
    else:
        h = SHA.new(msg)
    signer = PKCS1_v1_5.new(key)
    signature = signer.sign(h)
    signature = stringToBase64(signature)
    return signature




def split_rsa_key(key):
    key = str(key)
    return ''.join([('%s\n' % s) if ((i + 1) % 64 == 0) else s for i, s in enumerate(key)])


def get_format_pubkey(key):
    key = re.sub('\s', '', key)
    pub_key = split_rsa_key(key)
    return public_key_tpl % pub_key


# 将公钥字符串转为m2c的对象
def get_m2c_pub(pub_string):  
    return M2Crypto.RSA.load_pub_key_bio(M2Crypto.BIO.MemoryBuffer(pub_string))


# 公钥解密数据
def decrypt(data, m2c_pub, ilen=128):  
    _maxlength = ilen 
    data =data.decode("base64")
    l_dstr = "" 
    while len(data) > 0:
        s = data[:_maxlength]
        l_dstr += m2c_pub.public_decrypt(s, M2Crypto.RSA.pkcs1_padding)
        data = data[_maxlength:]
    return  l_dstr


#公钥签名认证
def pub_verify(data,sign,m2c_pub):
    m = M2Crypto.EVP.MessageDigest('sha1')
    m.update(data)
    digest = m.final()
    sign = sign.decode("base64")
    try:
        return m2c_pub.verify(digest,sign,algo='sha1') 
    except:
        return False


def DesEncrypt(text, Des_Key):
    Des_IV = "12345678"  # 自定IV向量
    k = des(Des_Key, mode=CBC, IV=Des_IV, pad=None, padmode=PAD_PKCS5)
    EncryptStr = k.encrypt(text)
    return base64.b64encode(EncryptStr)  # 转base64编码返回

def DesDecrypt(text, Des_Key):
    Des_IV = "12345678"  # 自定IV向量
    text = base64.b64decode(text)
    k = des(Des_Key, mode=CBC, IV=Des_IV, pad=None, padmode=PAD_PKCS5)
    return k.decrypt(text)
