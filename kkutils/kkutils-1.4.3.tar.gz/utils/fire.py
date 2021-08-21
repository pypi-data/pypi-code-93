#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Author: zhangkai
Email: kai.zhang1@nio.com
Last modified: 2019-09-04 13:32:01
'''
import asyncio
import inspect
import sys

from .base_utils import pprint
from .config_utils import Config


def Fire(component=None):
    kwargs = Config()
    params = [x for x in sys.argv[1:] if not x.startswith('--')]

    if component is None:
        modules = inspect.stack()[1].frame.f_globals
        module = modules[params[0]]
        if isinstance(module, type):
            func = getattr(module(), params[1])
            args = params[2:]
        else:
            func = module
            args = params[1:]
    else:
        if inspect.isclass(component):
            module = component()
            func = getattr(module, params[0])
            args = params[1:]
        elif not inspect.isfunction(component):
            func = getattr(component, params[0])
            args = params[1:]

    ret = func(*args, **kwargs)
    if inspect.isawaitable(ret):
        loop = asyncio.get_event_loop()
        ret = loop.run_until_complete(ret)
    pprint(ret)
