from math import ceil
import re


def str_to_int(s):
    try:
        if s is not None and isinstance(s, str):
            s = s.replace(",", "").replace(" ", "").replace("$", "")
            return int(str(s))
        else:
            return int(s)
    except Exception as e:
        print(e)
        return None


def str_to_float(s):
    try:
        if s is not None and (isinstance(s, str)):
            s = s.replace(",", "").replace(" ", "").replace("$", "")
            return float(str(s))
        else:
            return float(s)
    except Exception as  e:
        print(e)
        return None


def extract_decimal(val):
    if val:
        result = re.search(r"(\d[\d\,\.]*)", str(val),  re.I | re.S)
        if result:
            return result.group(1)
    return None


def get_ceil(nominator, denominator):
    try:
        return int(ceil(1.0*nominator/denominator))
    except Exception as e:
        print(e)
        return None