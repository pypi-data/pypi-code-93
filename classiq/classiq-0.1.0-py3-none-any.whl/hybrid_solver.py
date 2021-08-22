from typing import Optional

from classiq import api_wrapper
from classiq_interface.hybrid import result as hybrid_result, vqe_problem
from classiq_interface.generator import result as generation_result


class HybridSolver:
    def __init__(
        self,
        circuit: generation_result.GeneratedCircuit,
        preferences: Optional[vqe_problem.VQEPreferences] = None,
    ):
        if preferences is None:
            preferences = vqe_problem.VQEPreferences()

        self._problem = vqe_problem.VQEProblem(
            vqe_preferences=preferences, ansatz=circuit.qasm, cost_data=circuit.metadata
        )

    @property
    def problem(self):
        return self._problem

    async def solve(self) -> hybrid_result.SolverResults:
        wrapper = api_wrapper.ApiWrapper()
        result = await wrapper.call_hybrid_task(problem=self._problem)

        if result.status != hybrid_result.HybridStatus.SUCCESS:
            raise Exception(f"Solving failed: {result.details}")

        return result.details
