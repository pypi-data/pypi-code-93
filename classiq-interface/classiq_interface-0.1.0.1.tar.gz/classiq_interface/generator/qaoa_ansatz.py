from typing import Type, Tuple

import pydantic

from classiq_interface.generator.problem_properties import (
    ProblemProperties,
)
from classiq_interface.generator.function_params import FunctionParams
from classiq_interface.hybrid.mht_qaoa_input import MhtQaoaInput
from classiq_interface.hybrid.problem_input import ProblemInput


class QaoaAnsatz(FunctionParams):
    """
    Parametric circuit for an optimization QAOA solver.
    """

    problem_properties: ProblemProperties = pydantic.Field(
        description="Properties of the " "combinatorial optimization " "problem"
    )

    @pydantic.validator("problem_properties")
    def validate_problem_supported_by_qaoa(cls, problem_properties):
        _SUPPORTED_PROBLEM_TYPES: Tuple[Type[ProblemInput], ...] = (MhtQaoaInput,)

        if not isinstance(problem_properties.problem, _SUPPORTED_PROBLEM_TYPES):
            raise ValueError(
                f"{problem_properties.problem.name} is not supported by QAOA"
            )

        return problem_properties
