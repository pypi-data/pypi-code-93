from pprint import pformat


class PrettyDict(dict):
    def __str__(self):
        return pformat(self, sort_dicts=False)


class PrettyList(list):
    def __str__(self):
        return pformat(self, sort_dicts=False)


class Pretty:
    def __new__(cls, item):
        if isinstance(item, list):
            item = PrettyList(item)
        elif isinstance(item, dict):
            item = PrettyDict(item)
        return item


def prettify(function):
    def wrapper(*args, **kwargs):
        item = function(*args, **kwargs)
        return Pretty(item)

    return wrapper
