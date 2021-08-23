import os


def makedirs(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def fullname(c):
    module = c.__module__
    if module == "builtins":
        return c.__qualname__  # avoid outputs like 'builtins.str'
    return module + "." + c.__qualname__
