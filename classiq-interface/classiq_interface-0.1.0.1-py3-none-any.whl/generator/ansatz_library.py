from typing import Optional, Union, List, Literal

from classiq_interface.hybrid.mht_input import (
    EntanglementStructureType,
    EntanglementBlocksType,
    RotationBlocksType,
)

import pydantic


class CustomAnsatzArgs(pydantic.BaseModel):
    num_qubits: int


class SeparateU3Args(CustomAnsatzArgs):
    pass


class HypercubeArgs(CustomAnsatzArgs):
    layer_count: int = 2


class EntanglingLayersArgs(CustomAnsatzArgs):
    layer_count: int = (2,)


class RandomArgs(CustomAnsatzArgs):
    gate_count: int = (100,)
    gate_probabilities: dict = ({"cx": 0.5, "u": 0.5},)
    random_seed: int = None


class RandomTwoQubitGatesArgs(CustomAnsatzArgs):
    random_two_qubit_gate_count_factor: float = (1.0,)
    random_seed: int = None


class TwoLocalArgs(CustomAnsatzArgs):
    rotation_blocks: Optional[
        Union[RotationBlocksType, List[RotationBlocksType]]
    ] = RotationBlocksType.ry
    entanglement_blocks: Optional[
        Union[EntanglementBlocksType, List[EntanglementBlocksType]]
    ] = EntanglementBlocksType.cx
    entanglement: EntanglementStructureType = EntanglementStructureType.full
    reps: int = 3
