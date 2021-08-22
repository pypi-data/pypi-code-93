from typing import List, Literal, Optional

import numpy as np
import pydantic

from classiq_interface.generator import adjacency
from classiq_interface.hybrid.problem_input import ProblemInput, OptimizationProblemName


class MVCInput(ProblemInput):
    name: Literal[OptimizationProblemName.MVC] = pydantic.Field(
        default=OptimizationProblemName.MVC, description="Name of optimization problem."
    )
    n: pydantic.PositiveInt = pydantic.Field(
        default=..., description="Number of vertices in the graph."
    )
    k: pydantic.PositiveInt = pydantic.Field(
        default=..., description="Size of cover vertices subset."
    )
    adjacency_matrix: Optional[List[List[bool]]] = pydantic.Field(
        default=None, description="Graph adjacency matrix."
    )
    reps: pydantic.conint(ge=1) = pydantic.Field(
        default=3, description="Number of QAOA layers."
    )

    @pydantic.validator("adjacency_matrix", pre=True, always=True)
    def check_adjacency_matrix(cls, matrix, values):
        if matrix is None:
            matrix = adjacency.get_rand_adjacency_matrix(num_vertices=values["n"])
        array = np.array(matrix)
        if not array.shape[0] == array.shape[1]:
            raise ValueError("distance matrix must be square")
        if not np.allclose(array, array.T):
            raise ValueError("Adjacency matrix is not symmetric")
        if np.diag(array).any():
            raise ValueError("Diagonal of adjacency matrix is not zero")
        return matrix

    def is_valid_cost(self, cost: float) -> bool:
        adjacency_matrix = np.array(self.adjacency_matrix)
        num_edges = np.sum(adjacency_matrix) / 2
        _MIN_COST = 0

        return _MIN_COST <= cost <= num_edges
