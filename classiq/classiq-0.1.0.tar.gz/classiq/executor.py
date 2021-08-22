"""Executor module, implementing facilities for executing circuits using Classiq platform."""
from typing import Union

from classiq import api_wrapper
from classiq_interface.execute import result as exc_result, execute_problem
from classiq_interface.execute.result import (
    FinanceSimulationResults,
    GroverSimulationResults,
)
from classiq_interface.generator import result as gen_result


class Executor:
    """Executor is the entry point for executing circuits on multiple hardware."""

    def __init__(
        self,
        circuit: gen_result.GeneratedCircuit,
        preferences: execute_problem.GeneralPreferences,
    ) -> None:
        """Init self.

        Args:
            circuit (): The circuit to execute.
            preferences (): Execution preferences, such as number of shots.
        """
        self._problem = execute_problem.ExecuteProblem(
            problem_preferences=preferences, problem_data=circuit.metadata
        )

    # TODO needs to be changed to execution result
    async def execute(
        self,
    ) -> Union[FinanceSimulationResults, GroverSimulationResults, str]:
        """Executes the circuit and returns its results.

        Returns:
            The execution results, corresponding to the executed circuit type.
        """
        wrapper = api_wrapper.ApiWrapper()
        execute_result = await wrapper.call_execute_task(problem=self._problem)

        if execute_result.status != exc_result.ExecutionStatus.SUCCESS:
            raise Exception(f"Execution failed: {execute_result.details}")

        return execute_result.details
