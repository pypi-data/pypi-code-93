import pydantic

from classiq_interface.generator import problem_name_mapping
from classiq_interface.hybrid.encoding_type import EncodingType
from classiq_interface.hybrid.problem_input import ProblemInput


class ProblemProperties(pydantic.BaseModel):
    problem: ProblemInput = pydantic.Field(
        default=..., description="Problem input data"
    )
    encoding_type: EncodingType = pydantic.Field(
        default=None, description="Various encoding types to the combinatorial problem."
    )

    @pydantic.validator("problem", pre=True)
    def check_problem(cls, problem):
        if isinstance(problem, dict) and problem.get("name") is None:
            return problem

        return problem_name_mapping.parse_problem_input(problem)

    @pydantic.validator("encoding_type", always=True)
    def check_encoding_type(cls, encoding_type, values):
        if encoding_type:
            return encoding_type
        problem = values.get("problem")
        if not problem:
            return encoding_type
        encoding_type = problem_name_mapping.ENCODING_TYPE_DEFAULT[type(problem)]
        return encoding_type
