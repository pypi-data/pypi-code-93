from typing import Union

from classiq_interface.hybrid.encoding_type import EncodingType
from classiq_interface.hybrid.mht_input import MHTInput
from classiq_interface.hybrid.mht_qaoa_input import MhtQaoaInput
from classiq_interface.hybrid.mvc_input import MVCInput
from classiq_interface.hybrid.problem_input import OptimizationProblemName, ProblemInput
from classiq_interface.hybrid.tsp_input import TSPInput

PROBLEM_INPUT_MAPPING = {
    OptimizationProblemName.TSP: TSPInput,
    OptimizationProblemName.MVC: MVCInput,
    OptimizationProblemName.MHT: MHTInput,
    OptimizationProblemName.MhtQaoa: MhtQaoaInput,
}

ENCODING_TYPE_DEFAULT = {
    TSPInput: EncodingType.NODES,
    MVCInput: EncodingType.DICKE,
    MHTInput: EncodingType.SERIAL,
    MhtQaoaInput: EncodingType.SERIAL,
}

for e in OptimizationProblemName:
    assert e in PROBLEM_INPUT_MAPPING, "verify all problem inputs are accessible"

for e in PROBLEM_INPUT_MAPPING.values():
    assert e in ENCODING_TYPE_DEFAULT, "verify all problem inputs are accessible"


def parse_problem_input(problem: Union[dict, ProblemInput]) -> ProblemInput:
    problem_name = (
        problem.name if isinstance(problem, ProblemInput) else problem["name"]
    )
    return PROBLEM_INPUT_MAPPING[problem_name].parse_obj(obj=problem)
