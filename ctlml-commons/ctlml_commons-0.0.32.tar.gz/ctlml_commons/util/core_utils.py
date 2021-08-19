from typing import Any


def get_class(path: str) -> Any:
    tokens = path.split(".")
    klass = tokens[-1]
    modules = ".".join(tokens[:-1])

    module = __import__(modules, fromlist=[klass])
    return getattr(module, klass)
