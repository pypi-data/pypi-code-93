# coding: utf-8
from __future__ import unicode_literals, absolute_import

import os

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db.utils import DEFAULT_DB_ALIAS
from fias.weights import weights

DATABASE_ALIAS = getattr(settings, 'FIAS_DATABASE_ALIAS', DEFAULT_DB_ALIAS)

if DATABASE_ALIAS not in settings.DATABASES:
    raise ImproperlyConfigured('FIAS: database alias `{0}` was not found in DATABASES'.format(DATABASE_ALIAS))
elif DATABASE_ALIAS != DEFAULT_DB_ALIAS and 'fias.routers.FIASRouter' not in settings.DATABASE_ROUTERS:
    raise ImproperlyConfigured('FIAS: for use external database add `fias.routers.FIASRouter`'
                               ' into `DATABASE_ROUTERS` list in your settings.py')

user_weights = getattr(settings, 'FIAS_SB_WEIGHTS', {})
if not isinstance(user_weights, dict):
    raise ImproperlyConfigured('FIAS_SB_WEIGHTS should be a dict type')

weights.update(user_weights)

SUGGEST_BACKEND = getattr(settings, 'FIAS_SUGGEST_BACKEND', 'fias.suggest.backends.noop')
SUGGEST_VIEW = getattr(settings, 'FIAS_SUGGEST_VIEW', 'fias:suggest')
SUGGEST_AREA_VIEW = getattr(settings, 'FIAS_SUGGEST_AREA_VIEW', 'fias:suggest-area')

# SUDS Proxy Support
_http_proxy = os.environ.get('http_proxy')
_https_proxy = os.environ.get('https_proxy')

PROXY = {}
if _http_proxy:
    PROXY['http'] = _http_proxy
if _https_proxy:
    PROXY['https'] = _https_proxy
