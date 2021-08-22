import abc
from enum import Enum
from typing import Tuple, Union

import pydantic

from classiq_interface.generator import convert_phase, probability
from classiq_interface.generator.circuit_outline import Qubit


class Slide(pydantic.BaseModel, abc.ABC):
    """
    A sequence of same-type-constructs, on a sequence of qubits.
    """

    # TODO: Verify values are not greater than max index.
    slide_targets: Tuple[Qubit, ...] = pydantic.Field(
        default=..., description="The sequence of qubits to assign the construct on."
    )

    @pydantic.validator("slide_targets")
    def slide_targets_uniqueness(cls, value):
        if len(value) != len(set(value)):
            raise ValueError("must not contain repetitions")

        return value


class PhaseDistributionType(str, Enum):
    UNIFORM = "uniform"
    RANDOM = "random"


class PhaseDistribution(pydantic.BaseModel):
    distribution_type: PhaseDistributionType
    total_phase: pydantic.confloat(ge=0)
    # The phase here is converted to degrees within phase slide.


class PhaseSlide(Slide):
    slide_phases: Union[PhaseDistribution, Tuple[float, ...], Tuple[int, ...]]

    @pydantic.validator("slide_phases", always=True)
    def phases_validator(cls, slide_phases, values):
        slide_targets = values.get("slide_targets")
        if slide_targets is None:
            # In that case, don't do any validation.
            return slide_phases

        if isinstance(slide_phases, PhaseDistribution):
            slide_phases = cls.distribute_phase(
                phase_distribution=slide_phases, entries_count=len(slide_targets)
            )

        if len(slide_phases) != len(slide_targets):
            raise ValueError("phases and targets length mismatch")

        slide_phases_rad: Tuple[int, ...] = tuple(
            convert_phase.rad_to_deg(i) for i in slide_phases
        )

        return slide_phases_rad

    @staticmethod
    def distribute_phase(
        phase_distribution: PhaseDistribution, entries_count: int
    ) -> Tuple[float, ...]:
        if phase_distribution.distribution_type == PhaseDistributionType.UNIFORM:
            return (
                convert_phase.to_canonical_phase(
                    phase_distribution.total_phase / entries_count
                ),
            ) * entries_count

        if phase_distribution.distribution_type == PhaseDistributionType.RANDOM:
            random_probability = probability.random_probability(
                options_count=entries_count
            )
            return tuple(
                convert_phase.to_canonical_phase(phase_distribution.total_phase * prob)
                for prob in random_probability
            )

        assert (
            False
        ), f"non supported distribution type {phase_distribution.distribution_type}"
