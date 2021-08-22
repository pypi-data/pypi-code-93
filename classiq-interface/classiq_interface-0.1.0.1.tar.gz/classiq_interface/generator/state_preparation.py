from enum import Enum
from typing import Tuple, Optional, Dict, Union

import pydantic
from classiq_interface.generator.function_params import (
    FunctionParams,
    DefaultOutputNames,
    DefaultInputNames,
)
from classiq_interface.generator.preferences.optimization import (
    StatePrepOptimizationMethod,
)
from classiq_interface.generator.range_types import NonNegativeFloatRange


class Metrics(str, Enum):
    KL = "KL"
    L2 = "L2"
    L1 = "L1"
    MAX_PROBABILITY = "MAX_PROBABILITY"


def is_power_of_two(pmf):
    n = len(pmf)
    is_power_of_two = (n != 0) and (n & (n - 1) == 0)
    if not is_power_of_two:
        raise ValueError("Probabilities length must be power of 2")
    return pmf


class PMF(pydantic.BaseModel):
    pmf: Tuple[pydantic.confloat(ge=0, le=1), ...]

    @pydantic.validator("pmf")
    def is_sum_to_one(cls, pmf):
        # n = len(pmf)
        # is_power_of_two = (n != 0) and (n & (n - 1) == 0)
        # if not is_power_of_two:
        #     raise ValueError("Probabilities length must be power of 2")
        if round(sum(pmf), 8) != 1:
            raise ValueError("Probabilities do not sum to 1")
        return pmf

    _is_pmf_valid = pydantic.validator("pmf", allow_reuse=True)(is_power_of_two)


class GaussianMoments(pydantic.BaseModel):
    mu: float
    sigma: pydantic.confloat(gt=0)


class GaussianMixture(pydantic.BaseModel):
    gaussian_moment_list: Tuple[GaussianMoments, ...]


StatePreparationOutputs = DefaultOutputNames
StatePreparationInputs = DefaultInputNames


class StatePreparation(FunctionParams):
    probabilities: Union[PMF, GaussianMixture]
    depth_range: Optional[NonNegativeFloatRange] = NonNegativeFloatRange(
        lower_bound=0, upper_bound=1e100
    )
    cnot_count_range: Optional[NonNegativeFloatRange] = NonNegativeFloatRange(
        lower_bound=0, upper_bound=1e100
    )
    error_metric: Optional[Dict[Metrics, NonNegativeFloatRange]] = pydantic.Field(
        default_factory=lambda: {
            Metrics.KL: NonNegativeFloatRange(lower_bound=0, upper_bound=1e100)
        }
    )
    optimization_method: Optional[
        StatePrepOptimizationMethod
    ] = StatePrepOptimizationMethod.KL
    num_qubits: Optional[int] = None
    is_uniform_start: bool = True

    @pydantic.validator("is_uniform_start")
    def is_uniform_start_validator(cls, is_uniform_start, values):
        if not is_uniform_start:
            if Metrics.KL in values["error_metric"]:
                raise ValueError("Error Metric for non-uniform start can be L1 ans L2")
            if StatePrepOptimizationMethod.KL in values["optimization_method"]:
                raise ValueError(
                    "Optimization method for non-uniform start can be L1 ans L2"
                )
        return is_uniform_start

    @pydantic.root_validator()
    def validate_num_qubits(cls, values):
        num_qubits = values["num_qubits"]
        probabilities = values["probabilities"]
        if isinstance(probabilities, GaussianMixture) and num_qubits is None:
            raise ValueError("num_qubits must be set when using gaussian mixture")

        return values

    class Config:
        extra = "forbid"
