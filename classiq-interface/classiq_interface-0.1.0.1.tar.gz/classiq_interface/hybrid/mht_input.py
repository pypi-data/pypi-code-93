import enum
from typing import Literal, Union, List, Optional, Any

import pydantic

from classiq_interface.hybrid.problem_input import ProblemInput, OptimizationProblemName


class RotationBlocksType(str, enum.Enum):
    rx = "rx"
    ry = "ry"
    rz = "rz"


class EntanglementBlocksType(str, enum.Enum):
    cx = "cx"
    cy = "cy"
    cz = "cz"


class EntanglementStructureType(str, enum.Enum):
    linear = "linear"
    full = "full"
    circular = "circular"
    sca = "sca"


class MHTInput(ProblemInput):
    name: Literal[OptimizationProblemName.MHT] = pydantic.Field(
        default=OptimizationProblemName.MHT, description="Name of optimization problem."
    )
    plot_count: pydantic.conint(gt=0, lt=20) = pydantic.Field(
        default=3, description="Number of plots."
    )
    max_track_count: pydantic.conint(gt=0, lt=20) = pydantic.Field(
        default=2, description="Maximum number of tracks."
    )
    penalty_energy: Union[int, float] = pydantic.Field(
        default=10,
        description="Penalty energy for invalid solutions, "
        "The value effects the converges rate."
        " Small positive values are preferred",
    )
    plot_track_matching: Optional[List[int]] = pydantic.Field(
        default=None, description="known matching between plots and tracks"
    )
    reps: int = pydantic.Field(
        default=3,
        description="Amount of repetitions of a rotation layer and entanglement layer.",
    )
    rotation_blocks: Union[
        RotationBlocksType, List[RotationBlocksType]
    ] = pydantic.Field(
        default=RotationBlocksType.ry,
        description="The gates used in the rotation layer.",
    )
    entanglement_blocks: Union[
        EntanglementBlocksType, List[EntanglementBlocksType]
    ] = pydantic.Field(
        default=EntanglementBlocksType.cx,
        description="The gates used in the entanglement layer.",
    )
    entanglement: EntanglementStructureType = pydantic.Field(
        default=EntanglementStructureType.full,
        description="Structure of entanglement layer.",
    )
    data_for_cost_server: Any = pydantic.Field(
        default=None,
        description="Additional data to forward to the external"
        " cost server, e.g. configuration",
    )

    @pydantic.validator("plot_track_matching", always=True)
    def init_plot_track_matching(cls, plot_track_matching, values):
        plot_count = values.get("plot_count")
        if plot_count is None:
            raise ValueError("Plot count is mandatory")
        if plot_track_matching is None:
            plot_track_matching = [0] * plot_count

        return plot_track_matching

    def is_valid_cost(self, cost: float) -> bool:
        return True
