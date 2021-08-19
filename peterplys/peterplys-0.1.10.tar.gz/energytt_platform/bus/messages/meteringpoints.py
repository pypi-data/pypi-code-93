from typing import Optional
from dataclasses import dataclass

from energytt_platform.bus import Message
from energytt_platform.models.common import Address
from energytt_platform.models.tech import TechnologyCodes
from energytt_platform.models.meteringpoints import \
    MeteringPoint, MeteringPointDelegate


@dataclass
class MeteringPointUpdate(Message):
    """
    A MeteringPoint has either been added to the system,
    or an existing MeteringPoint has had its details updated.
    """
    meteringpoint: MeteringPoint


@dataclass
class MeteringPointRemoved(Message):
    """
    A MeteringPoint has been remove from the system.
    # TODO Advice to perform Clean-up?
    """
    gsrn: str


@dataclass
class MeteringPointTechnologyUpdate(Message):
    """
    Updates technology codes for a MeteringPoint.

    Providing None value for 'codes' indicates that services should
    reset/forget existing technology codes.
    """
    gsrn: str
    codes: Optional[TechnologyCodes]


@dataclass
class MeteringPointAddressUpdate(Message):
    """
    Updates address for a MeteringPoint.

    Providing None value for 'address' indicates that services should
    reset/forget existing address.
    """
    gsrn: str
    address: Optional[Address]


# -- Delegates ---------------------------------------------------------------


@dataclass
class MeteringPointDelegateGranted(Message):
    """
    An actor (identified by its subject) has been delegated
    access to a MeteringPoint.
    """
    delegate: MeteringPointDelegate


@dataclass
class MeteringPointDelegateRevoked(Message):
    """
    An actor (identified by its subject) has had its delegated
    access to a MeteringPoint revoked.
    """
    delegate: MeteringPointDelegate
