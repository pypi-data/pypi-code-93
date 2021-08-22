from typing import List

import pydantic

from classiq_interface.generator.circuit_outline import Qubit


class SatConstraint(pydantic.BaseModel):
    variables: pydantic.conlist(item_type=Qubit, min_items=1)
    truth_table: List[bool]

    @pydantic.validator("truth_table")
    def truth_table_validator(cls, truth_table):
        if not any(truth_table):
            raise ValueError("truth table must contain at least 1 true value")

        return truth_table

    @pydantic.root_validator(skip_on_failure=True)
    def combinations_length_validator(cls, values):
        variables, truth_table = values.get("variables"), values.get("truth_table")

        assert (
            variables is not None and truth_table is not None
        ), "These can not be none, as skip_on_failure is True."

        possible_combinations_count = 2 ** len(variables)
        if len(truth_table) != possible_combinations_count:
            raise ValueError(
                f"length of truth_table truth table must be {possible_combinations_count}"
            )

        return values


class SatProblem(pydantic.BaseModel):
    variables_count: pydantic.PositiveInt
    constraints: List[SatConstraint]
