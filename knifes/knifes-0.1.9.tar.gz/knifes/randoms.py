import random
import string
from knifes.digests import md5
import uuid


def random_str(length=4):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))


def make_unique_str():
    return md5(str(uuid.uuid1()))