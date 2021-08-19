from energytt_platform.bus import message_registry

from .auth import UserOnboarded
from .tech import TechnologyUpdate, TechnologyRemoved
from .measurements import (
    MeasurementUpdate,
    MeasurementRemoved,
)
from .meteringpoints import (
    MeteringPointUpdate,
    MeteringPointRemoved,
    MeteringPointTechnologyUpdate,
    MeteringPointAddressUpdate,
    MeteringPointDelegateGranted,
    MeteringPointDelegateRevoked,
)


message_registry.add(

    # Authentication
    UserOnboarded,

    # Technology
    TechnologyUpdate,
    TechnologyRemoved,

    # Measurements
    MeasurementUpdate,
    MeasurementRemoved,

    # MeteringPoints
    MeteringPointUpdate,
    MeteringPointRemoved,
    MeteringPointTechnologyUpdate,
    MeteringPointAddressUpdate,
    MeteringPointDelegateGranted,
    MeteringPointDelegateRevoked,

)
