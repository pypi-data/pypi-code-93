import base64
import hashlib
import logging
import binascii
from Crypto.Cipher import AES
from pyDes import des, PAD_PKCS5, ECB, CBC
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import algorithms

logger = logging.getLogger(__name__)


def xor(bin1, bin2) -> str:
    """基本XOR方法，用来在特定情况下代替python的^符号"""
    return '0' if bin1 == bin2 else '1'


def md5(s, salt='', encoding='utf-8') -> str:
    if isinstance(s, str):
        return hashlib.md5((s + salt).encode(encoding=encoding)).hexdigest()
    else:
        return hashlib.md5(s).hexdigest()


def base64Encode(s) -> bytes:
    s = str(s)
    return base64.b64encode(s.encode('utf-8'))


def base64Decode(s) -> str:
    s = str(s)
    return base64.b64decode(s).decode('utf-8')


def bytes_decode(b: bytes, default='utf-8') -> str:
    import cchardet
    try:
        res = b.decode(default)
    except:
        detect = cchardet.detect(b)
        code = detect['encoding']
        res = b.decode(code)
    return res


def asc2int(sx) -> (str, tuple):
    """获取字符、字符串的ascii码值"""
    if not isinstance(sx, str):
        sx = str(sx)
    return ord(sx) if len(sx) == 1 else tuple(ord(x) for x in sx)


def asc2hex(asc_str) -> str:
    """把字符串转换为16进制字符"""
    asc_hex_arr = [[int2hex(asc2int(i))] for i in asc_str]
    result = ''
    for hex_c in asc_hex_arr:
        hex_c = capitalize_hex(hex_c[0])
        result = result + hex_c
    return result


def int2hex(x: int) -> str:
    """10进制转16进制"""
    return hex(x)


def int2asc(x: int) -> str:
    """ascii码值转对应字符"""
    return chr(x)


def str2bytes(s: str) -> bytes:
    return s.encode('raw_unicode_escape')


def bytes_to_hex(bs: bytes) -> str:
    """bytes转16进制字符串"""
    # return ''.join(['%02X ' % b for b in bs]) #这样也可以
    result = ''
    for b_int_str in bs:
        b_hex_str = '%02X ' % b_int_str  # 另一种方式，把10进制字符串转换成16进制字符串
        result = result + capitalize_hex(b_hex_str)
    return result


def capitalize_bin(bin_str: str):
    """格式二进制字符串:去除ob和空格，并且如果不足8位，在前面添加0补齐"""
    bin_str = bin_str.replace('0b', '').replace(' ', '')
    if len(bin_str) % 8 == 0:
        pass
    else:
        prex = 8 - len(bin_str)
        bin_str = '0' * prex + bin_str
    return bin_str


def str2bin(s: str) -> str:
    """字符串转2进制字符串"""
    result = ''
    for i in s:
        result = result + capitalize_bin(bin(ord(i)))  # capitalizeBin_str(bin(ord(i)):把单个字符转换成二进制
    return result


def bin2str(b: str) -> str:
    """2进制转字符串"""
    b = b.replace('0b', '').replace(' ', '')
    if len(b) % 8 == 0:
        b_array = [b[i:i + 8] for i in range(0, len(b), 8)]
        # print(b_array)
        result = ''
        for i in b_array:
            result = result + chr(int(i, 2))  # chr(int(i, 2)):把二进制转化成单个字符
        return result
    else:
        raise ValueError


def bin2hex(bin_str) -> str:
    """2进制字符串转换成16进制字符串"""
    bin_str = capitalize_bin(bin_str)
    return capitalize_hex(int2hex(int(bin_str, 2)).replace('0x', ''))


def bin_xor_bin(bin_str1, bin_str2) -> str:
    """2进制字符串进行XOR计算"""
    bin_str1 = capitalize_bin(bin_str1)
    bin_str2 = capitalize_bin(bin_str2)
    if len(bin_str1) == len(bin_str2):
        result = ''
        for i in range(0, len(bin_str1)):
            result = result + xor(bin_str1[i], bin_str2[i])
        return result
    else:
        raise ValueError


def capitalize_hex(hex_str: str):
    """格式16进制字符串:去除0x和空格,并且如果字符串只有1位，在前面补0"""
    hex_str = hex_str.replace('0x', '').replace('0X', '').replace(' ', '')
    if len(hex_str) % 2 == 0:
        return hex_str
    elif len(hex_str) == 1:
        return '0' + hex_str
    else:
        raise ValueError


def hex_to_bytes(s: str) -> bytes:
    """16进制转bytes"""
    return binascii.a2b_hex(s)


def hex2int(x: str) -> int:
    """16进制转10进制"""
    return int(x, 16)


def hex2bin(hex_str: str) -> str:
    """16进制转2进制字符串"""
    hex_str = capitalize_hex(hex_str)
    return capitalize_bin(bin(hex2int(hex_str)))


def hex2asc(hex_str: str) -> str:
    hex_str = capitalize_hex(hex_str)
    hex_str_arr = hex2hex_arr(hex_str)
    result = ''
    for hex_c in hex_str_arr:
        hex_int = int(hex_c, 16)
        result = result + int2asc(hex_int)
    return result


def hex2hex_arr(hex_str: str) -> list:
    """把16进制字符串转换成2个2个一对的16进制数组"""
    hex_str = capitalize_hex(hex_str)
    hex_str_arr = [hex_str[i:i + 2] for i in range(0, len(hex_str), 2)]
    return hex_str_arr


def hex_xor_hex_str(hex_str1, hex_str2) -> str:
    """把16进制字符串进行XOR计算"""
    hex_str1 = capitalize_hex(hex_str1)
    hex_str2 = capitalize_hex(hex_str2)
    if len(hex_str1) == len(hex_str2):
        hex_arr1 = hex2hex_arr(hex_str1)  # 把16进制两两分组
        hex_arr2 = hex2hex_arr(hex_str2)
        result = ''
        for i in range(0, len(hex_arr1)):
            bin_str1 = hex2bin(hex_arr1[i])  # 16进制转换成2进制
            bin_str2 = hex2bin(hex_arr2[i])
            result_bin_str = bin_xor_bin(bin_str1, bin_str2)  # 2进制xor计算
            result_hex_str = bin2hex(result_bin_str)  # 2进制转换成16进制
            result = result + result_hex_str
        return result
    else:
        raise ValueError


def change_byte(byte_str, offset, new_byte):
    """改变bytes中指定位置的byte"""
    if offset > len(byte_str):
        exit()
    result = b''
    i_num = 0
    for i in byte_str:
        i = hex_to_bytes(hex(i))
        if i_num == offset:
            byte_s = new_byte
        else:
            byte_s = i
        result = result + byte_s
        i_num = i_num + 1
    return result


class CryptoModel:
    """
    AES加密类
    """

    def __init__(self, key: str, iv: str, mode=AES.MODE_CBC):
        self.key = key.encode()
        self.iv = iv.encode()
        self.mode = mode

    @staticmethod
    def padding(text: bytes):
        padding_0a = (16 - len(text) % 16) * b' '
        return text + padding_0a

    @staticmethod
    def pkcs7_padding(data):
        if not isinstance(data, bytes):
            data = data.encode()

        padder = padding.PKCS7(algorithms.AES.block_size).padder()

        padded_data = padder.update(data) + padder.finalize()

        return padded_data

    @staticmethod
    def pkcs7_unpadding(padded_data):
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        data = unpadder.update(padded_data)

        try:
            uppadded_data = data + unpadder.finalize()
        except ValueError:
            raise Exception('无效的加密信息!')
        else:
            return uppadded_data

    def aes_encode(self, text: bytes):
        obj = AES.new(self.key, self.mode, self.iv)
        data = self.pkcs7_padding(text)
        return obj.encrypt(data)

    def aes_decode(self, data: bytes):
        obj = AES.new(self.key, self.mode, self.iv)
        return obj.decrypt(data).rstrip(b"\x01").\
            rstrip(b"\x02").rstrip(b"\x03").rstrip(b"\x04").rstrip(b"\x05").\
            rstrip(b"\x06").rstrip(b"\x07").rstrip(b"\x08").rstrip(b"\x09").\
            rstrip(b"\x0a").rstrip(b"\x0b").rstrip(b"\x0c").rstrip(b"\x0d").\
            rstrip(b"\x0e").rstrip(b"\x0f").rstrip(b"\x10")

    def encrypt(self, data):
        ' 加密函数 '
        cryptor = AES.new(self.key, self.mode, self.iv)
        return binascii.b2a_hex(cryptor.encrypt(data)).decode()

    def decrypt(self, data):
        ' 解密函数 '
        cryptor = AES.new(self.key, self.mode, self.iv)
        return cryptor.decrypt(binascii.a2b_hex(data)).decode()


class DESModel:
    """
    DES加密类
    """

    def __init__(self, key, iv=None, mode=ECB):
        """
        :param key: Key
        :param iv: Initialization vector
        :param mode: algorithm
        """
        if mode == ECB and iv is not None:
            raise ValueError('MODE ECB can not IV')

        self.des = des(key=key, mode=mode, IV=iv, padmode=PAD_PKCS5)

    def encrypt(self, data, **kwargs):
        res = self.des.encrypt(data, **kwargs)
        return binascii.b2a_hex(res)

    def decrypt(self, data, **kwargs):
        return self.des.decrypt(binascii.a2b_hex(data), **kwargs)


if __name__ == '__main__':
    key = 'cb05362287a2404b'
    iv = 'a03f3b8977a72276'
    from base64 import b64decode, b64encode
    # b = b64decode('Z6v9HtLIECjzMNLwwywkdg==')
    a = CryptoModel(key=key, iv=iv)
    b = b64encode(a.aes_encode('{"web": {}}'))
    print(b)
    print(a.aes_decode(b64decode(b.decode())))

