from typing import List, Sequence, Optional
from enum import IntEnum
from staliro.results import Result
from dataclasses import dataclass

class SamplingMethod(IntEnum):
    BAYESIAN = 1
    GAUSSIAN = 2

class PartXBehavior(IntEnum):
    FALSIFICATION = 1


@dataclass
class PartitioningOptions:
    subregion_file: str
    region_dimension: int
    num_partition: int
    miscoverage_level: float
    num_sampling: int
    level: Sequence[float]
    min_volume: float
    max_budget: int
    fal_num: float
    n_model: int
    n_bo: int
    n_b: int
    sample_method: SamplingMethod
    part_num: int
    continue_sampling_budget: int


@dataclass(frozen=True)
class PartitioningResult(Result):
    seed: int
    time_taken: float
    theta_plus: Sequence[float]
    theta_minus: Sequence[float]
    theta_undefined: Sequence[float]
    evl: Sequence[float]
    budgets: Sequence[int]
    falsification_volumes: Sequence[float]
    p_iter: Sequence[float]
    number_subregion: Sequence[float]
    fal_ems: float
    fal_con: Optional[list] = None
