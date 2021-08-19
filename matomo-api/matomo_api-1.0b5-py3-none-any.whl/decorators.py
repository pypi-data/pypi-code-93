"""Decorators for the Matomo API modules and module-methods."""

import requests
from functools import wraps

MODULES = []


def module_decorator(mod_class):
    """Wrapper for all API module classes"""
    def __init__(self, url, token):
        self._url = url
        self._args = {'token_auth': token}
    setattr(mod_class, '__init__', __init__)
    MODULES.append(mod_class.__name__)
    return mod_class


def method_decorator(mod_meth):
    """Wrapper for all API method functions"""
    @wraps(mod_meth)
    def wrapper(self, qry_pars):
        self._args['module'] = 'API'  # following ambivalent use of module :(
        module = self.__class__.__name__.removeprefix('Mod')
        method = mod_meth.__name__
        self._args['method'] = f'{module}.{method}'
        self._args |= qry_pars
        return requests.get(self._url, self._args)
    return wrapper

