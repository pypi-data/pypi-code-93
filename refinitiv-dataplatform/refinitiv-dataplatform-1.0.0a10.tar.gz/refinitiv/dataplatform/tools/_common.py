def get_from_path(obj, path, delim="."):
    splitted = path.split(delim)
    for k in splitted:
        if hasattr(obj, "get"):
            obj = obj.get(k)
        elif iterable(obj) and is_int(k):
            obj = obj[int(k)]
    return obj


def is_int(obj):
    if isinstance(obj, str):
        try:
            int(obj)
        except Exception:
            return False
        else:
            return True
    return isinstance(obj, int)


def iterable(obj):
    try:
        iter(obj)
    except Exception:
        return False
    else:
        return True


def urljoin(*pieces):
    # first piece have a leading slash
    if pieces and len(pieces[0]) > 1 and pieces[0][0] == "/":
        pieces = ("/",) + pieces
    # last piece have a trailing slash
    if pieces and len(pieces[-1]) > 1 and pieces[-1][-1] == "/":
        pieces = pieces + ("/",)
    return "/".join(s.strip("/") for s in pieces)


def is_any_defined(*args):
    return any(args)


def is_all_defined(*args):
    return all(args)


def is_all_same_type(item_type, iterable):
    return all(isinstance(item, item_type) for item in iterable)


def make_counter():
    i = 0

    def counter():
        nonlocal i
        i += 1
        return i

    return counter


def get_response_reason(response):
    if hasattr(response, "reason_phrase"):
        assert not hasattr(response, "reason")
        return response.reason_phrase
    elif hasattr(response, "reason"):
        return response.reason
    return "unknown reason"


class cached_property(object):
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, cls=None):
        result = instance.__dict__[self.func.__name__] = self.func(instance)
        return result
