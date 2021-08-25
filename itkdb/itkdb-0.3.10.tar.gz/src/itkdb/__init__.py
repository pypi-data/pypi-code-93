from .version import __version__
from . import core
from . import exceptions
from . import models
from .client import Client
from .settings import settings


def listInstitutions():
    return models.institution.make_institution_list(
        core.Session().get('listInstitutions').json()['pageItemList']
    )


__all__ = [
    '__version__',
    'Client',
    'core',
    'exceptions',
    'models',
    'settings',
    'listInstitutions',
]
