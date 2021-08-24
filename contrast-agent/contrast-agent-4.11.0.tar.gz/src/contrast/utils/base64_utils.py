# -*- coding: utf-8 -*-
# Copyright © 2021 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import base64

from contrast.extern import six

PY3 = six.PY3


def base64_encode(to_encode):
    """
    Allows you to encode string to Base64

    Works with Python 2 and 3
    """
    if PY3 and isinstance(to_encode, str):
        input_object = to_encode.encode("utf-8")
    else:
        input_object = to_encode

    output_object = base64.b64encode(input_object)

    if PY3:
        return output_object.decode("ascii")

    return output_object


def base64_decode(to_decode):
    """
    Allows you to decode Base64 to str

    Works with Python 2 and 3
    """
    output_object = base64.urlsafe_b64decode(six.ensure_str(to_decode))
    return six.ensure_str(output_object)
