from datetime import datetime
from typing import Type

from decouple import config
from hashlib import sha1

from pydantic import BaseModel


def clean_signature_value(value: str):
    """
    According to the docs spaces are removed
    """
    return str(value).replace(" ", "")


def build_signature(**kwargs):
    ret = ""

    sorted_kwargs_list = sorted(kwargs.items(), key=lambda t: t[0])

    for key, value in sorted_kwargs_list:
        if value is not None:
            ret += str(key) + clean_signature_value(value)
    return ret


def build_param(method, **kwargs):

    api_key = config("ONLINE_AFSPRAKEN_KEY")
    api_secret = config("ONLINE_AFSPRAKEN_SECRET")

    salt = int(datetime.now().timestamp())
    signature_raw = (
        # build_signature(method=method, **kwargs) + "method" + method + api_secret + str(salt)
        build_signature(method=method, **kwargs)
        + api_secret
        + str(salt)
    )
    signature_encoded = signature_raw.encode()
    signature = sha1(signature_encoded)

    params = {
        "api_key": api_key,
        "api_salt": salt,
        "api_signature": signature.hexdigest(),
        "method": method,
    }
    return dict(params, **kwargs)


def parse_schema(
    response_data, parse_key: str, schema: Type[BaseModel], enforce_list=False
):
    if "Objects" not in response_data:
        return []

    if enforce_list and not isinstance(response_data["Objects"][parse_key], list):
        response_data["Objects"][parse_key] = [response_data["Objects"][parse_key]]

    response_object = schema.parse_obj(response_data)

    if response_object:
        return response_object.objects[parse_key]
    return []
