from typing import Optional

from classiq_interface.generator.arithmetic import ArithmeticOracle
from classiq_interface.generator.function_params import FunctionParams
from classiq_interface.generator.state_preparation import StatePreparation


class GroverOperator(FunctionParams):
    oracle: ArithmeticOracle
    state_preparation: Optional[StatePreparation] = None
    diffuser: Optional[str] = None

    def create_io_enums(self):
        self._input_names = self.oracle._input_names
        self._output_names = self.oracle._input_names

    class Config:
        extra = "forbid"
