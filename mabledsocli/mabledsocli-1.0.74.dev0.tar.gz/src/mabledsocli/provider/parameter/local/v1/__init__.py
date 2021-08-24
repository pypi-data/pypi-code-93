__package__ = 'mabledsocli.provider.parameter.local.v1'
from .main import LocalParameterProvider
from mabledsocli.providers import Providers
Providers.register(LocalParameterProvider())
