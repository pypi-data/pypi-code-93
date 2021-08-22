import enum

import pydantic


class OptimizationProblemName(str, enum.Enum):
    TSP = "TSP"
    MVC = "MVC"
    MHT = "MHT"
    MhtQaoa = "MHT QAOA"


class ProblemInput(pydantic.BaseModel):
    name: OptimizationProblemName

    class Config:
        # Using this class allows sending this object as a json to the
        # frontEnd with all the objects that inheritance from this class
        extra = "allow"

    def is_valid_cost(self, cost: float) -> bool:
        raise NotImplementedError
