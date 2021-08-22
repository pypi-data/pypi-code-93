from typing import List, Literal
from typing import Optional

import numpy as np
import pydantic

from classiq_interface.generator import distance
from classiq_interface.hybrid.problem_input import ProblemInput, OptimizationProblemName


class TSPInput(ProblemInput):
    name: Literal[OptimizationProblemName.TSP] = pydantic.Field(
        default=OptimizationProblemName.TSP, description="Name of optimization problem."
    )
    num_cities: pydantic.conint(gt=1) = pydantic.Field(
        default=..., description="Number of cities in the TSP problem."
    )
    distance_matrix: Optional[List[List[float]]] = pydantic.Field(
        default=None, description="Matrix consisting of distance between the cities."
    )

    @pydantic.root_validator
    def init_distance_matrix(cls, values):
        num_cities, distance_matrix = values.get("num_cities"), values.get(
            "distance_matrix"
        )
        if num_cities is None:
            raise ValueError("Num cities is mandatory")
        if distance_matrix is None:
            values["distance_matrix"] = distance.get_rand_distance_matrix(
                num_points=num_cities
            )

        return values

    @pydantic.validator("distance_matrix")
    def check_distance_matrix(cls, matrix):
        array = np.array(matrix)
        if not array.shape[0] == array.shape[1]:
            raise ValueError("distance matrix must be square")
        if not np.all(array >= 0):
            raise ValueError("All the elements of distance matrix must be non-negative")
        if not np.allclose(array, array.T):
            raise ValueError("Distance Matrix is not symmetric")
        return matrix

    def is_valid_cost(self, cost: float) -> bool:
        distance_matrix = np.array(self.distance_matrix)
        num_cities = distance_matrix.shape[0]
        max_distance = np.amax(distance_matrix)
        max_cost = max_distance * (num_cities - 1)
        _MIN_COST = 0

        return _MIN_COST < cost and approx_lte(x=cost, y=max_cost)


def approx_lte(x, y) -> bool:
    return x < y or np.isclose(x, y)
