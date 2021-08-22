import enum
from typing import Dict, Type

import pydantic

from classiq_interface.generator.ansatz_library import (
    TwoLocalArgs,
    SeparateU3Args,
    HypercubeArgs,
    EntanglingLayersArgs,
    RandomArgs,
    RandomTwoQubitGatesArgs,
)


class CustomAnsatzType(str, enum.Enum):
    TwoLocal = "TwoLocal"
    SeparateU3 = "SeparateU3"
    Hypercube = "Hypercube"
    EntanglingLayers = "EntanglingLayers"
    Random = "Random"
    RandomTwoQubitGates = "RandomTwoQubitGates"


CUSTOM_ANSATZ_ARGS_MAPPING: Dict[CustomAnsatzType, Type[pydantic.BaseModel]] = {
    CustomAnsatzType.TwoLocal: TwoLocalArgs,
    CustomAnsatzType.SeparateU3: SeparateU3Args,
    CustomAnsatzType.Hypercube: HypercubeArgs,
    CustomAnsatzType.EntanglingLayers: EntanglingLayersArgs,
    CustomAnsatzType.Random: RandomArgs,
    CustomAnsatzType.RandomTwoQubitGates: RandomTwoQubitGatesArgs,
}

# AnastazData: Dict
# CUSTOM_ANSATZ_MAPPING : Ansatz, Args (class per ansatz)
# Args.parse_obj(**AnasatzData)
