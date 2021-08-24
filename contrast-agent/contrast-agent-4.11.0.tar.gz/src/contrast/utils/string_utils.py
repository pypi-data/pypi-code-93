# -*- coding: utf-8 -*-
# Copyright © 2021 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.extern import six

from contrast.extern import structlog as logging

logger = logging.getLogger("contrast")


def truncate(value, default="", length=256):
    """
    Truncate to `length` characters
    """
    if value is None:
        return default

    return value[:length]


def truncated_signature(value):
    """
    Get a log-friendly representation of a potentially long string. This function
    will truncate the string if necessary.

    First, we truncate the input to 60 characters - if this does happen, we'll also add
    `[TRUNCATED]` to the output. We then append the string's `id`. The string is
    converted to its most readable form using __repr__, which means that any newlines
    or invisible chars (like BEL) will be converted to something nice and readable.

    examples:
    'This is some string' (id=4443462824)
    'Here is a very long string that is longer th' [TRUNCATED] (id=4443294816)

    :param value: string whose truncated signature we want
    :return: string representation of the input value, truncated to 60 chars with
        its `id` appended as well. On any failure, return only the id.
    """
    try:
        append_truncate = ""

        if isinstance(value, bytearray):
            value = bytes(value)

        if len(value) > 60:
            value = value[:60]
            append_truncate = " [TRUNCATED]"

        value = six.ensure_str(value, errors="ignore")
        return "{!r}{} (id={})".format(value, append_truncate, id(value))
    except Exception as e:
        logger.debug("Failed to truncate string: %s", e)
        return "(id={})".format(id(value))


def index_of_any(value, search_chars):
    """
    Find the first index of a char in a string
    :param value: string to search
    :param search_chars: strings to search for
    :return: index if found else -1
    """

    for sc in search_chars:

        index = value.find(sc)

        if index != -1:
            return index

    return -1


def ends_with_any(value, strings):
    """
    Returns True if any of the strings are at the end of the value
    """
    return any(value.endswith(item) for item in strings)


def equals_ignore_case(this, that):
    return this.lower() == that.lower()


def protobuf_safe(value):
    return "" if value is None else value


def ensure_string(value):
    return value if isinstance(value, six.string_types) else value.decode("utf-8")
