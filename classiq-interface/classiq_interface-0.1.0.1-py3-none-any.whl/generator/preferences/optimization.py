from enum import Enum

import pydantic


class StatePrepOptimizationMethod(str, Enum):
    KL = "KL"
    L2 = "L2"
    L1 = "L1"
    MAX_PROBABILITY = "MAX_PROBABILITY"
    RANDOM = "RANDOM"


class OptimizationType(str, Enum):
    DEPTH = "depth"
    TWO_QUBIT_GATES = "two_qubit_gates"


class Optimization(pydantic.BaseModel):
    approximation_error: pydantic.confloat(ge=0, lt=1) = 0
    optimization_type: OptimizationType = OptimizationType.DEPTH
