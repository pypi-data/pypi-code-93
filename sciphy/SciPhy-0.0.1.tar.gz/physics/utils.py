from errors import *


def classify(obj: object):
    return f"'{str(type(obj))[8:-2].split('.')[-1]}'"