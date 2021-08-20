import re


def to_camel_case(text):
    """ Transform snake_case to CamelCase """
    return re.sub(r"(_\w)", lambda x: x.group(1)[1:].upper(), text)
