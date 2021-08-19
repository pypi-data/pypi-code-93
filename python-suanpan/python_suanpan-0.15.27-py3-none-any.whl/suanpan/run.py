# coding=utf-8
from __future__ import absolute_import, print_function

import argparse
import contextlib
import copy
import faulthandler
import sys

from suanpan.imports import imports
from suanpan.utils import env as spenv


def run(component, *args, **kwargs):
    if isinstance(component, str):
        component = f"{component[:-3]}.app" if component.endswith(".py") else component
        component = imports(component)
    with env(**kwargs.pop("env", {})):
        return component.start(*args, **kwargs)


@contextlib.contextmanager
def env(**kwargs):
    old = copy.deepcopy(spenv.environ)
    spenv.update(kwargs)
    yield spenv.environ
    spenv.update(old)


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("component")
    _args, _rest = parser.parse_known_args()

    sys.argv = sys.argv[:1]
    return run(_args.component, *_rest)


if __name__ == "__main__":
    faulthandler.enable()
    cli()
