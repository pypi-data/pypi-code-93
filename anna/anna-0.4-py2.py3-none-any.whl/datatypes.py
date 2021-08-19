# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import six

# Note that if the data types are changed to something which is not JSON serializable (as for
# example numpy.int64 on Python3) then the corresponding case needs to be covered in
# `utils.convert_to_json_serializable_object`. Otherwise the string representation of
# `Configurable` will induce a TypeError as it uses json.dumps for describing the object.
_float = float
_int = int

representations = {
    'number': _float,
    'integer': _int,
}

number = representations['number']
integer = representations['integer']


def convert_to(representation):
    def converter(item):
        if isinstance(representation, six.text_type):
            return representations[representation](item)
        else:
            return representation(item)
    return converter
