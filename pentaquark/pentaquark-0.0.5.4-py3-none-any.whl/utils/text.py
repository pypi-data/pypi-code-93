
def remove_prefix(text, prefix):
    """
    Remove prefix from text

    :param str text:
    :param str prefix:
    :return:
    :rtype: str
    """
    if not text.startswith(prefix):
        return text
    return text[len(prefix):]


def remove_suffix(text, suffix):
    """
    Remove suffix from text

    :param str text:
    :param str suffix:
    :return:
    :rtype: str
    """
    if not text.endswith(suffix):
        return text
    return text[:len(text) - len(suffix)]


def to_upper_camel_case_single(snake_str):
    snake_str = remove_suffix(snake_str, "s")
    components = snake_str.split('_')
    return ''.join(x.title() for x in components)
