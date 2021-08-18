import hashlib
import random
import string


def md5(data):
    if isinstance(data, str):
        data = data.encode()
    return hashlib.md5(data).hexdigest()


def random_string(slen=10):
    letters = string.ascii_letters \
        + string.digits  \
        + string.whitespace  \
        + string.punctuation
    return ''.join(random.sample(letters, slen))


def ok(data: dict):
    return "OK" == data["errMsg"] \
        or "Ok" == data["errMsg"] \
        or "oK" == data["errMsg"] \
        or "ok" == data["errMsg"]
