import shortuuid
import numpy as np


def get_type_name(obj):
    type_name = obj.__class__.__module__ + "." + obj.__class__.__name__
    if type_name in ["builtins.module", "__builtin__.module"]:
        return obj.__name__
    else:
        return type_name


def generate_uuid():
    generated_uuid = shortuuid.ShortUUID(alphabet=list("0123456789abcdefghijklmnopqrstuvwxyz"))
    return generated_uuid.random(8)


def to_uint8(data):
    dmin = np.min(data)
    if dmin < 0:
        data = (data - np.min(data)) / np.ptp(data)
    if np.max(data) <= 1.0:
        data = (data * 255).astype(np.int32)

    return data.clip(0, 255).astype(np.uint8)
