"""Analyzer module, implementing facilities for analyzing circuits using Classiq platform."""
from classiq import api_wrapper
from classiq_interface.analyzer import result as analysis_result, analysis_params
from classiq_interface.generator import result as generator_result


class Analyzer:
    """Analyzer is the wrapper object for all analysis capabilities."""

    def __init__(self, circuit: generator_result.GeneratedCircuit):
        """Init self.

        Args:
            circuit (): The circuit to be analyzed.
        """
        self._params = analysis_params.AnalysisParams(qasm=circuit.qasm)

    async def analyze(self) -> analysis_result.Analysis:
        """Runs the circuit analysis.

        Returns:
            The analysis result.
        """
        wrapper = api_wrapper.ApiWrapper()
        result = await wrapper.call_analysis_task(params=self._params)

        if result.status != analysis_result.AnalysisStatus.SUCCESS:
            raise Exception(f"Analysis failed: {result.details}")

        return result.details
