from __future__ import annotations

from datetime import datetime
from typing import List, Sequence
from enum import IntEnum

from staliro.options import Options
from staliro.optimizers import OptimizationFn, Optimizer
from staliro.results import Result, Run

import pathlib

from .models import SamplingMethod, PartitioningOptions, PartitioningResult, PartXBehavior
from .continued_sampling import part_optimize_with_continued_sampling
from .controlled_budget import part_optimize_with_controlled_budget

def _optimize(func: ObjectiveFn, options: Options, optimizer_options: PartitioningOptions) -> PartitioningRun:
    subregions = [bound.astuple() for bound in options.bounds]
    start_time = datetime.now()

    replications = 1
    iterations = 1
    if optimizer_options.continue_sampling_budget is not None:
        result = part_optimize_with_continued_sampling(
            subregion_file=optimizer_options.subregion_file,
            subregion=subregions,
            region_dimension=optimizer_options.region_dimension,
            num_partition=optimizer_options.num_partition,
            confidence_level=0.05,
            func=func,
            num_sampling=optimizer_options.num_sampling,
            levels=optimizer_options.level,
            replications=replications,
            iterations=iterations,
            min_volume=optimizer_options.min_volume,
            budget=optimizer_options.max_budget,
            fal_num=optimizer_options.fal_num,
            n_model=optimizer_options.n_model,
            n_bo=optimizer_options.n_bo,
            n_b=optimizer_options.n_b,
            sample_method=optimizer_options.sample_method,
            part_num=optimizer_options.part_num,
            continue_sampling_budget=optimizer_options.continue_sampling_budget,
            seed=12222
        )
    else:
        result = part_optimize_with_controlled_budget(
            subregion_file=optimizer_options.subregion_file,
            subregion=subregions,
            region_dimension=optimizer_options.region_dimension,
            num_partition=optimizer_options.num_partition,
            confidence_level=0.05,
            func=func,
            num_sampling=optimizer_options.num_sampling,
            levels=optimizer_options.level,
            replications=replications,
            iterations=iterations,
            min_volume=optimizer_options.min_volume,
            budget=optimizer_options.max_budget,
            fal_num=optimizer_options.fal_num,
            n_model=optimizer_options.n_model,
            n_bo=optimizer_options.n_bo,
            n_b=optimizer_options.n_b,
            sample_method=optimizer_options.sample_method,
            part_num=optimizer_options.part_num,
            seed=12222
        )

    end_time = datetime.now()

    partitioning_result = PartitioningResult(
        seed=result.seed,
        time_taken=start_time - end_time,
        theta_plus=result.theta_plus,
        theta_minus=result.theta_minus,
        theta_undefined=result.theta_undefined,
        evl=result.evl,
        budgets=result.budgets,
        falsification_volumes=result.falsification_volumes,
        p_iter=result.p_iter,
        number_subregion=result.number_subregion,
        fal_ems=result.fal_ems,
        options=None,
        runs=[])

    return partitioning_result


def partitioning(
    func: ObjectiveFn,
    options: Options,
    optimizer_options: PartitioningOptions
) -> List[PartitioningResult]:
    return _optimize(func, options, optimizer_options)

class PartX(Optimizer[Run]):
    def __init__(self, **kwargs):
        self.seed = 122222
        self.optimizer_options = PartitioningOptions(
            subregion_file=kwargs['subregion_file'],
            region_dimension=kwargs['region_dimension'],
            num_partition=kwargs['num_partition'],
            miscoverage_level=kwargs['miscoverage_level'],
            num_sampling=kwargs['num_sampling'],
            level=kwargs['level'],
            min_volume=kwargs['min_volume'],
            max_budget=kwargs['max_budget'],
            fal_num=kwargs['fal_num'],
            n_model=kwargs['n_model'],
            n_bo=kwargs['n_bo'],
            n_b=kwargs['n_b'],
            sample_method=kwargs['sample_method'],
            part_num=kwargs['part_num'],
            continue_sampling_budget=kwargs['continue_sampling_budget']
        )


    def optimize(self, func: OptimizationFn, 
                 options: Options) -> PartitioningRun:
        return _optimize(func, options, self.optimizer_options)
