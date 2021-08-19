""" Diffusion services package. """
from typing import Type, Mapping

from .abstract import Service, InboundService, OutboundService, ServiceValue
from .exceptions import ServiceError, UnknownServiceError
from .messaging import MessagingSend, MessagingReceiverControlRegistration
from .session import SystemPing, UserPing
from .topics import Subscribe


def get_by_id(service_id: int) -> Type[Service]:
    """ Retrieve a service class based on its ID number. """
    return Service.get_by_id(service_id)


def get_by_name(service_name: str) -> Type[Service]:
    """ Retrieve a service class based on its name. """
    return Service.get_by_name(service_name)


class ServiceLocator(dict, Mapping[str, Service]):
    """A mapping of services used by a feature.

    Lazily instantiates a service when requested.
    """

    def __getattr__(self, item: str) -> Service:
        return self[item]

    def __getitem__(self, item: str) -> Service:
        item = item.upper()
        if item not in self:
            self[item] = Service.get_by_name(item)()
        return super().__getitem__(item)

    def __iter__(self):
        return iter(self.items())
