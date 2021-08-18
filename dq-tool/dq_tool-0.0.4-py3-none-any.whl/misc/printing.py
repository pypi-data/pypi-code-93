"""Functions related to pretty printing"""
import json
import re

from .yaml import get_yaml

_DICT_PP_INDENT = 4


def pretty_repr(d: dict) -> str:
    """A pretty repr string out of a dictionary"""
    return json.dumps(d, indent=_DICT_PP_INDENT)


def pretty_print(d: dict) -> None:
    """Print nicely with indent"""
    print(pretty_repr(d))


def yamlize(d: dict) -> str:
    """Turn a dict into a yaml string - human but not necesarilly machine readable."""
    yaml_str = (
        get_yaml()
        .dump(d)
        .replace('"', '')
        .replace('\\', '')
    )
    # get rid of the weird apostrophes around the whole lines
    return re.sub(r"^(\s*)-(\s*)'(.*)'$", r"\1-\2\3", yaml_str, flags=re.MULTILINE)
