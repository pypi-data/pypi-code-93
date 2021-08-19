from __future__ import annotations

from hashlib import md5
from json import dump
from typing import TypedDict, List, Any, Dict

from attr import asdict
from staliro.results import Iteration, Run, Result


class IterationDict(TypedDict, total=False):
    sample: List[float]
    robustness: float
    sample_hash: str


class RunDict(TypedDict):
    run: int
    result: Any
    iterations: List[IterationDict]


class ResultDict(TypedDict):
    runs: List[RunDict]
    options: Dict[str, Any]


def _iter_dict(iteration: Iteration, include_hash: bool = True) -> IterationDict:
    if not include_hash:
        return IterationDict(
            sample=list(iteration.sample),
            robustness=iteration.cost,
        )
        
    return IterationDict(
        sample=iteration.sample.tolist(),
        robustness=iteration.cost,
        sample_hash=md5(iteration.sample.tobytes()).hexdigest(),
    )


def _run_dict(num: int, run: Run[Any, Iteration], include_hash: bool = True) -> RunDict:
    return RunDict(
        run=num,
        result=run.result,
        iterations=[_iter_dict(iteration, include_hash) for iteration in run.history],
    )


def _result_dict(result: Result[Any, Iteration], include_hash: bool = True) -> ResultDict:
    run_dicts = [_run_dict(num, run, include_hash) for num, run in enumerate(result.runs)]
    options_dict = asdict(result.options)

    return ResultDict(runs=run_dicts, options=options_dict)


def store_result(result: Result[Any, Iteration], filename: str, with_hash: bool = True) -> None:
    with open(filename, "w") as json_file:
        dump(_result_dict(result, include_hash=with_hash), json_file)
