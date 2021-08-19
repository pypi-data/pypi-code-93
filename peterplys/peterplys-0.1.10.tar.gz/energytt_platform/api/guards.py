from typing import List
from abc import abstractmethod
from dataclasses import dataclass

from energytt_platform.serialize import Serializable

from .context import Context


@dataclass
class Issuer(Serializable):
    id: str
    public_key: str


class EndpointGuard(object):

    @abstractmethod
    def validate(self, context: Context):
        raise NotImplementedError


# class ServiceGuard(EndpointGuard):
#     """
#     Allows only specific services to access this endpoint.
#     """
#     def __init__(self, *services: Service):
#         self.services = services
#
#
# class IssuerGuard(EndpointGuard):
#     """
#     Allows only specific issuers to access this endpoint.
#     """
#     def __init__(self, *services: Service):
#         self.services = services


class ScopedGuard(EndpointGuard):
    """
    Allows only clients with specific scopes granted.
    """
    def __init__(self, *scopes: str):
        self.scopes = scopes


class Bouncer(object):
    def validate(self, context: Context, guards: List[EndpointGuard]):
        raise NotImplementedError


# s1 = ServiceGuard(
#     Service(name='Service A'),
#     Service(name='Service B'),
# )
#
# s2 = ScopedGuard(
#     'meteringpoints.read',
#     'measurements.read',
#     'gc.read',
#     'gc.transfer',
# )


# -- Singletons --------------------------------------------------------------

bouncer = Bouncer()
