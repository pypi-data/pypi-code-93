# -*- coding: utf-8 -*-
import hashlib
import os

from number import (
    u64, u8, i64,
)


def create_seed_from_string(secret):
    """
    通过普通字符串创建长度为32的字节数组
    :param secret: 普通字符串
    :return: 字节数组
    """
    result = [u8(0)] * 32
    hash_ = hashlib.sha256(secret).hexdigest()
    for i in range(32):
        result[i] = int(hash_[i * 2:(i + 1) * 2], 16)
    return result


def create_byte_list_from_byte_list_by_sha256(byte_list):
    result = [u8(0)] * 32
    hash_ = hashlib.sha256(bytearray(byte_list)).hexdigest()
    for i in range(32):
        result[i] = int(hash_[i * 2:(i + 1) * 2], 16)
    return result


def nacl_sign_keypair_from_seed(seed):
    """
    通过普通字节数组生产秘钥对
    :param seed: 字节数组，来源于create_seed_from_string
    :return: 秘钥对
    """
    pk = [u8(0)] * crypto_sign_PUBLICKEYBYTES
    sk = [u8(0)] * crypto_sign_SECRETKEYBYTES
    # copy sk
    for i in range(crypto_sign_SEEDBYTES):
        sk[i] = seed[i]
    crypto_sign_keypair(pk, sk, True)
    # 将pk的值转为byte
    for i in range(len(pk)):
        pk[i] = u8(pk[i])
    return pk, sk


def nacl_sign_keypair_from_secret_key(secret_key):
    """
    通过普通字节数组生产秘钥对的秘钥生成二次秘钥
    :param secret_key: nacl_sign_keypair_from_seed方法生成的私钥
    :return:
    """
    sk = [u8(0)] * crypto_sign_SECRETKEYBYTES
    pk = [u8(0)] * crypto_sign_PUBLICKEYBYTES

    for i in range(len(sk)):
        sk[i] = secret_key[i]
    for i in range(len(pk)):
        pk[i] = secret_key[32 + i]
    return pk, sk


def nacl_sign_detached(msg, secret_key):
    signed_msg = nacl_sign(msg, secret_key)
    sig = [u8(0)] * crypto_sign_BYTES
    for i in range(len(sig)):
        sig[i] = signed_msg[i]
    return sig


def nacl_sign(msg, secret_key):
    signed_msg = [u8(0)] * (crypto_sign_BYTES + len(msg))
    crypto_sign(signed_msg, -1, msg, len(msg), secret_key)
    return signed_msg


def nacl_box_keypair_from_secret_key(secret_key):
    """
    通过普通字节数组生产秘钥对的秘钥生成二次秘钥(功能待验证)
    :param secret_key: nacl_sign_keypair_from_seed方法生成的私钥
    :return:
    """
    sk = [u8(0)] * crypto_box_SECRETKEYBYTES
    pk = [u8(0)] * crypto_box_PUBLICKEYBYTES
    for i in range(len(sk)):
        sk[i] = secret_key[i]
    crypto_scalarmult_base(pk, sk)
    return pk, sk


def crypto_sign_keypair(pk, sk, seeded):
    """
    加密签名秘钥
    :param pk: 公钥
    :param sk: 私钥
    :param seeded: 是否产生随机因子
    :return: 加密正确性 0正确 其他错误
    """
    d = [u8(0)] * 64
    p = [[i64(0)] * 16 for i in range(4)]
    if not seeded:
        randombytes(sk, 32)
    crypto_hash(d, sk, 0, len(sk), 32)
    d[0] &= 248
    d[31] &= 127
    d[31] |= 64
    scalarbase(p, d, 0, len(d))
    pack(pk, p)
    #
    for i in range(32):
        sk[i + 32] = u8(pk[i])
    return 0


def crypto_hash(out, m, m_off, m_len, n):
    """

    :param out: 字节数组
    :param m: 字节数组
    :param m_off: 整数
    :param m_len: 整数
    :param n: 整数
    :return:
    """
    h = [u8(0)] * 64
    x = [u8(0)] * 256
    b = n
    for i in range(64):
        h[i] = iv[i]
    crypto_hashblocks(h, m, m_off, m_len, n)
    n &= 127
    for i in range(256):
        x[i] = 0
    for i in range(n):
        x[i] = m[i + m_off]
    x[n] = 128
    n = 256 - 128 * (1 if n < 112 else 0)
    # x[n - 9] = unsigned_right_move(b, 61)
    # 采用普通右移
    x[n - 9] = b >> 61
    ts64(x, n - 8, len(x) - (n - 8), b << 3)
    crypto_hashblocks(h, x, 0, len(x), n)
    for i in range(64):
        out[i] = h[i]
    return 0


def crypto_hashblocks(x, m, m_off, m_len, n):
    """

    :param x: 字节数组
    :param m: 字节数组
    :param m_off: 整数
    :param m_len: 整数
    :param n: 整数
    :return:
    """
    z = [u64(0)] * 8
    b = [u64(0)] * 8
    a = [u64(0)] * 8
    w = [u64(0)] * 16
    t = u64(0)

    for i in range(8):
        z[i] = a[i] = dl64(x, 8 * i, len(x) - 8 * i)
    m_offset = m_off

    while n >= 128:
        for i in range(16):
            w[i] = dl64(m, 8 * i + m_offset, m_len - 8 * i)

        for i in range(80):
            for j in range(8):
                b[j] = u64(a[j])
            t = u64(a[7]) + Sigma1(u64(a[4])) + Ch(u64(a[4]), u64(a[5]), u64(a[6])) + K[i] + u64(w[i % 16])
            b[7] = t + Sigma0(a[0]) + Maj(a[0], a[1], a[2])
            b[3] += t
            for j in range(8):
                a[(j + 1) % 8] = u64(b[j])

            if i % 16 == 15:
                for j in range(16):
                    w[j] += u64(w[(j + 9) % 16]) + u64(sigma0(u64(w[(j + 1) % 16]))) + u64(
                        sigma1(u64(w[(j + 14) % 16])))
        for i in range(8):
            a[i] = u64(a[i]) + u64(z[i])

            z[i] = u64(a[i])
        m_offset += 128
        n -= 128

    for i in range(8):
        ts64(x, 8 * i, len(x) - 8 * i, z[i])

    return 0


def crypto_sign(sm, dummy, m, n, sk):
    d = [u8(0)] * 64
    h = [u8(0)] * 64
    r = [u8(0)] * 64

    x = [i64(0)] * 64

    p = [[i64(0)] * 16 for i in range(4)]

    crypto_hash(d, sk, 0, len(sk), 32)
    d[0] &= 248
    d[31] &= 127
    d[31] |= 64

    for i in range(n):
        sm[64 + i] = m[i]
    for i in range(32):
        sm[32 + i] = d[32 + i]
    crypto_hash(r, sm, 32, len(sm) - 32, n + 32)
    _reduce(r)
    scalarbase(p, r, 0, len(r))
    pack(sm, p)
    for i in range(32):
        sm[i + 32] = sk[i + 32]
    crypto_hash(h, sm, 0, len(sm), n + 64)
    _reduce(h)
    for i in range(64):
        x[i] = 0
    for i in range(32):
        x[i] = r[i] & 0xff
    for i in range(32):
        for j in range(32):
            x[i + j] += (h[i] & 0xff) * (d[j] & 0xff)

    modL(sm, 32, len(sm) - 32, x)

    return 0


def _reduce(r):
    x = [i64(0)] * 64

    for i in range(64):
        x[i] = r[i] & 0xff
    for i in range(64):
        r[i] = 0
    modL(r, 0, len(r), x)


def modL(r, r_off, r_len, x):
    carry = i64(0)
    for i in range(63, 31, -1):
        carry = 0
        for j in range(i - 32, i - 12):
            x[j] += carry - 16 * x[i] * L[j - (i - 32)]
            carry = (x[j] + 128) >> 8
            x[j] -= carry << 8
        j += 1
        x[j] += carry
        x[i] = 0

    carry = 0
    for j in range(32):
        x[j] += carry - (x[31] >> 4) * L[j]
        carry = x[j] >> 8
        x[j] &= 255

    for j in range(32):
        x[j] -= carry * L[j]

    for i in range(32):
        x[i + 1] += x[i] >> 8
        r[i + r_off] = x[i] & 255


def scalarbase(p, s, s_off, s_len):
    q = [[i64(0)] * 16 for i in range(4)]
    set25519(q[0], X)
    set25519(q[1], Y)
    set25519(q[2], gf1)
    M(q[3], 0, len(q[3]), X, 0, len(X), Y, 0, len(Y))
    scalarmult(p, q, s, s_off, s_len)


def scalarmult(p, q, s, s_off, s_len):
    set25519(p[0], gf0)
    set25519(p[1], gf1)
    set25519(p[2], gf1)
    set25519(p[3], gf0)
    for i in range(255, -1, -1):
        b = (s[i / 8 + s_off] >> (i & 7)) & 1
        cswap(p, q, b)
        add(q, p)
        add(p, p)
        cswap(p, q, b)


def cswap(p, q, b):
    for i in range(4):
        sel25519(p[i], 0, len(p[i]), q[i], 0, len(q[i]), b)


def add(p, q):
    a = [i64(0)] * 16
    b = [i64(0)] * 16
    c = [i64(0)] * 16
    d = [i64(0)] * 16
    e = [i64(0)] * 16
    f = [i64(0)] * 16
    g = [i64(0)] * 16
    h = [i64(0)] * 16
    t = [i64(0)] * 16

    p0 = p[0]
    p1 = p[1]
    p2 = p[2]
    p3 = p[3]

    q0 = q[0]
    q1 = q[1]
    q2 = q[2]
    q3 = q[3]
    Z(a, 0, len(a), p1, 0, len(p1), p0, 0, len(p0))
    Z(t, 0, len(t), q1, 0, len(q1), q0, 0, len(q0))
    M(a, 0, len(a), a, 0, len(a), t, 0, len(t))
    A(b, 0, len(b), p0, 0, len(p0), p1, 0, len(p1))
    A(t, 0, len(t), q0, 0, len(q0), q1, 0, len(q1))
    M(b, 0, len(b), b, 0, len(b), t, 0, len(t))
    M(c, 0, len(c), p3, 0, len(p3), q3, 0, len(q3))
    M(c, 0, len(c), c, 0, len(c), D2, 0, len(D2))
    M(d, 0, len(d), p2, 0, len(p2), q2, 0, len(q2))

    A(d, 0, len(d), d, 0, len(d), d, 0, len(d))
    Z(e, 0, len(e), b, 0, len(b), a, 0, len(a))
    Z(f, 0, len(f), d, 0, len(d), c, 0, len(c))
    A(g, 0, len(g), d, 0, len(d), c, 0, len(c))
    A(h, 0, len(h), b, 0, len(b), a, 0, len(a))

    M(p0, 0, len(p0), e, 0, len(e), f, 0, len(f))
    M(p1, 0, len(p1), h, 0, len(h), g, 0, len(g))
    M(p2, 0, len(p2), g, 0, len(g), f, 0, len(f))
    M(p3, 0, len(p3), e, 0, len(e), h, 0, len(h))


def pack(r, p):
    tx = [i64(0)] * 16
    ty = [i64(0)] * 16
    zi = [i64(0)] * 16

    inv25519(zi, 0, len(zi), p[2], 0, len(p[2]))

    M(tx, 0, len(tx), p[0], 0, len(p[0]), zi, 0, len(zi))
    M(ty, 0, len(ty), p[1], 0, len(p[1]), zi, 0, len(zi))

    pack25519(r, ty, 0, len(ty))

    r[31] ^= par25519(tx) << 7


def crypto_scalarmult_base(q, n):
    return crypto_scalarmult(q, n, _9)


def crypto_scalarmult(q, n, p):
    z = [u8(0)] * 32
    x = [i64(0)] * 80

    a = [i64(0)] * 16
    b = [i64(0)] * 16
    c = [i64(0)] * 16
    d = [i64(0)] * 16
    e = [i64(0)] * 16
    f = [i64(0)] * 16

    for i in range(31):
        z[i] = n[i]
    z[31] = (((n[31] & 127) | 64) & 0xff)
    z[0] &= 248
    unpack25519(x, p)
    for i in range(16):
        b[i] = x[i]
        d[i] = a[i] = c[i] = 0
    a[0] = d[0] = 1
    for i in range(254, -1, -1):
        r = (z[i >> 3] >> (i & 7)) & 1
        sel25519(a, 0, len(a), b, 0, len(b), r)
        sel25519(c, 0, len(c), d, 0, len(d), r)
        A(e, 0, len(e), a, 0, len(a), c, 0, len(c))
        Z(a, 0, len(a), a, 0, len(a), c, 0, len(c))
        A(c, 0, len(c), b, 0, len(b), d, 0, len(d))
        Z(b, 0, len(b), b, 0, len(b), d, 0, len(d))
        S(d, 0, len(d), e, 0, len(e))
        S(f, 0, len(f), a, 0, len(a))
        M(a, 0, len(a), c, 0, len(c), a, 0, len(a))
        M(c, 0, len(c), b, 0, len(b), e, 0, len(e))
        A(e, 0, len(e), a, 0, len(a), c, 0, len(c))
        Z(a, 0, len(a), a, 0, len(a), c, 0, len(c))
        S(b, 0, len(b), a, 0, len(a))
        Z(c, 0, len(c), d, 0, len(d), f, 0, len(f))
        M(a, 0, len(a), c, 0, len(c), _121665, 0, len(_121665))
        A(a, 0, len(a), a, 0, len(a), d, 0, len(d))
        M(c, 0, len(c), c, 0, len(c), a, 0, len(a))
        M(a, 0, len(a), d, 0, len(d), f, 0, len(f))
        M(d, 0, len(d), b, 0, len(b), x, 0, len(x))
        S(b, 0, len(b), e, 0, len(e))
        sel25519(a, 0, len(a), b, 0, len(b), r)
        sel25519(c, 0, len(c), d, 0, len(d), r)
    for i in range(16):
        x[i + 16] = a[i]
        x[i + 32] = c[i]
        x[i + 48] = b[i]
        x[i + 64] = d[i]
    inv25519(x, 32, len(x) - 32, x, 32, len(x) - 32)

    M(x, 16, len(x) - 16, x, 16, len(x) - 16, x, 32, len(x) - 32)

    pack25519(q, x, 16, len(x) - 16)

    return 0


def randombytes(c, s):
    """
    随机产生字节数组
    :param c: 字节数组存储对象
    :param s: 数组长度
    :return: void
    """
    c[:s] = bytearray(os.urandom(s))


crypto_secretbox_KEYBYTES = 32
crypto_secretbox_NONCEBYTES = 24
crypto_secretbox_ZEROBYTES = 32
crypto_secretbox_BOXZEROBYTES = 16
crypto_scalarmult_BYTES = 32
crypto_scalarmult_SCALARBYTES = 32
crypto_box_PUBLICKEYBYTES = 32
crypto_box_SECRETKEYBYTES = 32
crypto_box_BEFORENMBYTES = 32
crypto_box_NONCEBYTES = crypto_secretbox_NONCEBYTES
crypto_box_ZEROBYTES = crypto_secretbox_ZEROBYTES
crypto_box_BOXZEROBYTES = crypto_secretbox_BOXZEROBYTES
crypto_sign_BYTES = 64
crypto_sign_PUBLICKEYBYTES = 32
crypto_sign_SECRETKEYBYTES = 64
crypto_sign_SEEDBYTES = 32
crypto_hash_BYTES = 64

_0 = [u8(0)] * 16
_9 = [u8(0)] * 32
_9[0] = 9
gf0 = [i64(0)] * 16
gf1 = [i64(0)] * 16
gf1[0] = 1L
_121665 = [i64(0)] * 16
_121665[0] = 0xDB41
_121665[1] = 1

iv = [0x6a, 0x09, 0xe6, 0x67, 0xf3, 0xbc, 0xc9, 0x08,
      0xbb, 0x67, 0xae, 0x85, 0x84, 0xca, 0xa7, 0x3b,
      0x3c, 0x6e, 0xf3, 0x72, 0xfe, 0x94, 0xf8, 0x2b,
      0xa5, 0x4f, 0xf5, 0x3a, 0x5f, 0x1d, 0x36, 0xf1,
      0x51, 0x0e, 0x52, 0x7f, 0xad, 0xe6, 0x82, 0xd1,
      0x9b, 0x05, 0x68, 0x8c, 0x2b, 0x3e, 0x6c, 0x1f,
      0x1f, 0x83, 0xd9, 0xab, 0xfb, 0x41, 0xbd, 0x6b,
      0x5b, 0xe0, 0xcd, 0x19, 0x13, 0x7e, 0x21, 0x79]

D2 = [0xf159, 0x26b2, 0x9b94, 0xebd6,
      0xb156, 0x8283, 0x149a, 0x00e0,
      0xd130, 0xeef3, 0x80f2, 0x198e,
      0xfce7, 0x56df, 0xd9dc, 0x2406]

K = [0x428a2f98d728ae22L, 0x7137449123ef65cdL, 0xb5c0fbcfec4d3b2fL, 0xe9b5dba58189dbbcL,
     0x3956c25bf348b538L, 0x59f111f1b605d019L, 0x923f82a4af194f9bL, 0xab1c5ed5da6d8118L,
     0xd807aa98a3030242L, 0x12835b0145706fbeL, 0x243185be4ee4b28cL, 0x550c7dc3d5ffb4e2L,
     0x72be5d74f27b896fL, 0x80deb1fe3b1696b1L, 0x9bdc06a725c71235L, 0xc19bf174cf692694L,
     0xe49b69c19ef14ad2L, 0xefbe4786384f25e3L, 0x0fc19dc68b8cd5b5L, 0x240ca1cc77ac9c65L,
     0x2de92c6f592b0275L, 0x4a7484aa6ea6e483L, 0x5cb0a9dcbd41fbd4L, 0x76f988da831153b5L,
     0x983e5152ee66dfabL, 0xa831c66d2db43210L, 0xb00327c898fb213fL, 0xbf597fc7beef0ee4L,
     0xc6e00bf33da88fc2L, 0xd5a79147930aa725L, 0x06ca6351e003826fL, 0x142929670a0e6e70L,
     0x27b70a8546d22ffcL, 0x2e1b21385c26c926L, 0x4d2c6dfc5ac42aedL, 0x53380d139d95b3dfL,
     0x650a73548baf63deL, 0x766a0abb3c77b2a8L, 0x81c2c92e47edaee6L, 0x92722c851482353bL,
     0xa2bfe8a14cf10364L, 0xa81a664bbc423001L, 0xc24b8b70d0f89791L, 0xc76c51a30654be30L,
     0xd192e819d6ef5218L, 0xd69906245565a910L, 0xf40e35855771202aL, 0x106aa07032bbd1b8L,
     0x19a4c116b8d2d0c8L, 0x1e376c085141ab53L, 0x2748774cdf8eeb99L, 0x34b0bcb5e19b48a8L,
     0x391c0cb3c5c95a63L, 0x4ed8aa4ae3418acbL, 0x5b9cca4f7763e373L, 0x682e6ff3d6b2b8a3L,
     0x748f82ee5defb2fcL, 0x78a5636f43172f60L, 0x84c87814a1f0ab72L, 0x8cc702081a6439ecL,
     0x90befffa23631e28L, 0xa4506cebde82bde9L, 0xbef9a3f7b2c67915L, 0xc67178f2e372532bL,
     0xca273eceea26619cL, 0xd186b8c721c0c207L, 0xeada7dd6cde0eb1eL, 0xf57d4f7fee6ed178L,
     0x06f067aa72176fbaL, 0x0a637dc5a2c898a6L, 0x113f9804bef90daeL, 0x1b710b35131c471bL,
     0x28db77f523047d84L, 0x32caab7b40c72493L, 0x3c9ebe0a15c9bebcL, 0x431d67c49c100d4cL,
     0x4cc5d4becb3e42b6L, 0x597f299cfc657e2aL, 0x5fcb6fab3ad6faecL, 0x6c44198c4a475817L]

L = [
    0xed, 0xd3, 0xf5, 0x5c, 0x1a, 0x63, 0x12, 0x58,
    0xd6, 0x9c, 0xf7, 0xa2, 0xde, 0xf9, 0xde, 0x14,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0x10
]
X = [0xd51a, 0x8f25, 0x2d60, 0xc956,
     0xa7b2, 0x9525, 0xc760, 0x692c,
     0xdc5c, 0xfdd6, 0xe231, 0xc0a4,
     0x53fe, 0xcd6e, 0x36d3, 0x2169]

Y = [0x6658, 0x6666, 0x6666, 0x6666,
     0x6666, 0x6666, 0x6666, 0x6666,
     0x6666, 0x6666, 0x6666, 0x6666,
     0x6666, 0x6666, 0x6666, 0x6666]


def dl64(x, x_off, x_len):
    u = u64(0)
    for i in range(8):
        u = (u << 8) | (x[i + x_off] & 0xff)
    return u


def ts64(x, x_off, x_len, u):
    for i in range(7, -1, -1):
        x[i + x_off] = u8(u)
        u = u >> 8


def M(o, o_off, o_len, a, a_off, a_len, b, b_off, b_len):
    t = [i64(0)] * 31
    for i in range(31):
        t[i] = 0
    for i in range(16):
        for j in range(16):
            t[i + j] += a[i + a_off] * b[j + b_off]
    for i in range(15):
        t[i] += 38 * t[i + 16]
    for i in range(16):
        o[i + o_off] = t[i]
    car25519(o, o_off, o_len)
    car25519(o, o_off, o_len)


def A(o, o_off, o_len, a, a_off, a_len, b, b_off, b_len):
    for i in range(16):
        o[i + o_off] = a[i + a_off] + b[i + b_off]


def R(x, c):
    '''u64 R(u64 x, int c)'''
    return x >> c | (u64(x) << (64 - c))


def S(o, o_off, o_len, a, a_off, a_len):
    M(o, o_off, o_len, a, a_off, a_len, a, a_off, a_len)


def Z(o, o_off, o_len, a, a_off, a_len, b, b_off, b_len):
    for i in range(16):
        o[i + o_off] = a[i + a_off] - b[i + b_off]


def Ch(x, y, z):
    '''u64 Ch(u64 x, u64 y, u64 z)'''
    return (u64(x) & u64(y)) ^ (~u64(x) & u64(z))


def Maj(x, y, z):
    '''u64 Maj(u64 x, u64 y, u64 z)'''
    return (u64(x) & u64(y)) ^ (u64(x) & u64(z)) ^ (u64(y) & u64(z))


def Sigma0(x):
    '''u64 Sigma0(u64 x)'''
    return R(x, 28) ^ R(x, 34) ^ R(x, 39)


def Sigma1(x):
    '''u64 Sigma1(u64 x)'''
    rnt = R(x, 14) ^ R(x, 18) ^ R(x, 41)
    return rnt


def sigma0(x):
    '''u64 sigma0(u64 x)'''
    return R(x, 1) ^ R(x, 8) ^ (x >> 7)


def sigma1(x):
    '''u64 sigma1(u64 x)'''
    return R(x, 19) ^ R(x, 61) ^ (x >> 6)


def set25519(r, a):
    for i in range(16):
        r[i] = a[i]


def inv25519(o, o_off, o_len, i, i_off, i_len):
    c = [i64(0)] * 16
    for a in range(16):
        c[a] = i[a + i_off]
    for a in range(253, -1, -1):
        S(c, 0, len(c), c, 0, len(c))
        if a != 2 and a != 4:
            M(c, 0, len(c), c, 0, len(c), i, i_off, i_len)
    for a in range(16):
        o[a + o_off] = c[a]


def car25519(o, o_off, o_len):
    for i in range(16):
        o[i + o_off] += (1 << 16)

        c = o[i + o_off] >> 16
        o[(i + 1) * (1 if i < 15 else 0) + o_off] += c - 1 + 37 * (c - 1) * (1 if i == 15 else 0)

        o[i + o_off] -= (c << 16)


def par25519(a):
    d = [u8(0)] * 32
    pack25519(d, a, 0, len(a))
    return d[0] & 1


def pack25519(o, n, n_off, n_len):
    m = [i64(0)] * 16
    t = [i64(0)] * 16
    for i in range(16):
        t[i] = n[i + n_off]
    car25519(t, 0, len(t))
    car25519(t, 0, len(t))
    car25519(t, 0, len(t))
    for j in range(2):
        m[0] = t[0] - 0xffed
        for i in range(1, 15):
            m[i] = t[i] - 0xffff - ((m[i - 1] >> 16) & 1)
            m[i - 1] &= 0xffff
        m[15] = t[15] - 0x7fff - ((m[14] >> 16) & 1)
        b = ((m[15] >> 16) & 1)
        m[14] &= 0xffff
        sel25519(t, 0, len(t), m, 0, len(m), 1 - b)
    for i in range(16):
        o[2 * i] = (t[i] & 0xff)
        o[2 * i + 1] = (t[i] >> 8)


def sel25519(p, p_off, p_len, q, q_off, q_len, b):
    t = i64(0)
    c = i64(~(b - 1))
    for i in range(16):
        t = c & (p[i + p_off] ^ q[i + q_off])
        p[i + p_off] ^= t
        q[i + q_off] ^= t


def unpack25519(o, n):
    for i in range(16):
        o[i] = (n[2 * i] & 0xff) + ((n[2 * i + 1] << 8) & 0xffff)
    o[15] &= 0x7fff
