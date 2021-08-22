from typing import List, Optional, Dict, Any

import pydantic

from classiq_interface.generator.mcmt_method import McmtMethod
from classiq_interface.generator import custom_ansatz
from classiq_interface.generator.problem_properties import (
    ProblemProperties,
)
from classiq_interface.generator.function_params import FunctionParams
from classiq_interface.mixer import MixerType, MIXER_TYPES_DEFAULT
from classiq_interface.hybrid.encoding_type import EncodingType


class VQEAnsatz(FunctionParams):
    """
    Parametric circuit for an optimization VQE solver.
    """

    problem_properties: ProblemProperties = pydantic.Field(
        description="Properties of the " "combinatorial optimization " "problem"
    )
    mixer_types: List[MixerType] = pydantic.Field(
        default_factory=list,
        description="Ordered list of mixers applied in the ansatz.",
    )

    mcmt_method: McmtMethod = pydantic.Field(
        default=McmtMethod.vchain,
        description="multi controlled gates decomposition method.",
    )
    custom_ansatz_name: Optional[custom_ansatz.CustomAnsatzType] = pydantic.Field(
        default=None, description="A custom ansatz type"
    )
    custom_ansatz_args: Optional[Dict[str, Any]] = pydantic.Field(
        default=None, description="the arguments to the custom ansatz"
    )

    @pydantic.validator("mixer_types", always=True)
    def check_mixer_types(cls, mixer_types, values):
        if mixer_types is None:
            mixer_types = MIXER_TYPES_DEFAULT[type(values["problem"])]
        return mixer_types

    @pydantic.validator("mcmt_method", always=True)
    def check_mcmt_method(cls, mcmt_method, values):
        if mcmt_method is None:
            if values["encoding_type"] == EncodingType.SERIAL:
                return McmtMethod.vchain
            else:  # == EncodingType.NODES
                return McmtMethod.standard
        return mcmt_method

    @property
    def custom_ansatz_args_class(self):
        if self.custom_ansatz_name is None:
            return None
        return custom_ansatz.CUSTOM_ANSATZ_ARGS_MAPPING[self.custom_ansatz_name]
