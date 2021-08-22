import enum
from datetime import time, datetime
from typing import Union, Dict, Tuple, List, Optional

import pydantic

Plot = pydantic.conint(ge=0)
Track = pydantic.conint(ge=0)
MHTSolution = Dict[Plot, Track]


# We added this class to avoid issues with the schema, as it doesn't handle List[Tuple[int, int] or a union of
# List[List[int] with other things
class MhtSegmentSolution(pydantic.BaseModel):
    segment_list: List[Tuple[int, ...]]

    @pydantic.validator("segment_list")
    def verify_segments_are_legal(cls, segment_list):
        if any(len(segment) != 2 for segment in segment_list):
            raise ValueError("Segment list contains a segment with more than two plots")

        return segment_list


Solution = Union[Tuple[int, ...], MhtSegmentSolution, MHTSolution]


class HybridStatus(str, enum.Enum):
    SUCCESS = "success"
    ERROR = "error"


class SolverResult(pydantic.BaseModel):
    best_cost: float
    # TODO: add time units (like seconds)
    time: time
    solution: Solution


class SolutionData(pydantic.BaseModel):
    solution: Solution
    repetitions: pydantic.PositiveInt
    cost: float


class VQEIntermediateData(pydantic.BaseModel):
    utc_time: datetime = pydantic.Field(description="Time when the iteration finished")
    iteration_number: pydantic.PositiveInt = pydantic.Field(
        description="The iteration's number (evaluation count)"
    )
    parameters: List[float] = pydantic.Field(
        description="The optimizer parameters for the variational form"
    )
    mean_all_solutions: Optional[float] = pydantic.Field(
        default=None, description="The mean score of all solutions in this iteration"
    )
    mean_valid_solutions: Optional[float] = pydantic.Field(
        default=None, description="The mean score of the valid solutions."
    )
    solutions: List[SolutionData] = pydantic.Field(
        description="Solutions found in this iteration, their score and"
        "number of repetitions"
    )


class VQASolverResult(SolverResult):
    solution_distribution: Optional[List[SolutionData]]
    intermediate_results: Optional[List[VQEIntermediateData]]


class VQESolverResult(VQASolverResult):
    pass


class QAOASolverResult(VQASolverResult):
    preprocessed_graph: Dict
    solution_segment: List[Tuple[int, ...]]


class SolverResults(pydantic.BaseModel):
    vqe: Union[
        QAOASolverResult, VQESolverResult
    ]  # From most specific, to least specific
    classical: Optional[SolverResult]


class HybridResult(pydantic.BaseModel):
    status: HybridStatus
    details: Union[SolverResults, str]
