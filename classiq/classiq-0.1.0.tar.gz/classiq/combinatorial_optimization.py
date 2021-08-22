from typing import Optional
from pyomo.core import ConcreteModel

from classiq_interface.backend.backend_preferences import (
    BackendPreferences,
    IBMBackendPreferences,
)
from classiq_interface.combinatorial_optimization import (
    model_serializer,
    optimization_problem,
)
from classiq_interface.hybrid import result as hybrid_result
from classiq_interface.combinatorial_optimization.result import OptimizationResult
from classiq_interface.hybrid import vqe_problem
from classiq import api_wrapper


class CustomOptimization:
    def __init__(
        self,
        model: ConcreteModel,
        vqe_preferences: Optional[vqe_problem.VQEPreferences] = None,
        backend_preferences: Optional[BackendPreferences] = None,
    ):
        if vqe_preferences is None:
            vqe_preferences = vqe_problem.VQEPreferences()
        if backend_preferences is None:
            backend_preferences = IBMBackendPreferences(
                backend_service_provider="IBMQ", backend_name="aer_simulator"
            )

        self._serialized_model = model_serializer.to_json(model, return_dict=True)
        self._problem = optimization_problem.OptimizationProblem(
            serialized_model=self._serialized_model,
            vqe_preferences=vqe_preferences,
            backend_preferences=backend_preferences,
        )

    async def solve(self) -> OptimizationResult:
        wrapper = api_wrapper.ApiWrapper()
        result = await wrapper.call_combinatorial_optimization_task(
            problem=self._problem
        )

        if result.hybrid_result.status != hybrid_result.HybridStatus.SUCCESS:
            raise Exception(f"Solving failed: {result.hybrid_result.details}")

        return result
