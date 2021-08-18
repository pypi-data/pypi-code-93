import hashlib


def get_password_hash(password):
    password_bytes = bytes(password, encoding='utf-8')
    return hashlib.sha1(password_bytes).hexdigest()


def make_str_tuple(msg):
    """ Объединить все элементы кортежа в строку, разделить элементы пробелами"""
    return ' '.join(map(str, msg))
