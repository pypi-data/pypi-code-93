import enum
from classiq_interface.generator.problem_name_mapping import PROBLEM_INPUT_MAPPING
from classiq_interface.hybrid.mht_input import MHTInput
from classiq_interface.hybrid.mht_qaoa_input import MhtQaoaInput
from classiq_interface.hybrid.mvc_input import MVCInput
from classiq_interface.hybrid.tsp_input import TSPInput


class MixerType(enum.Enum):
    pass


class TSPMixerType(MixerType):
    CY_CUSTOM = "CY_CUSTOM"  # CY gates, with a target qubit that is part of a register encoding '11..1' domain range,
    # and a control qubit from another register
    CY_CUSTOM_INNER = "CY_CUSTOM_INNER"  # CY gates, with a target qubit that is part of a register encoding '11..1' domain
    # range, and a control qubit from the same register
    CZ = "CZ"  # CZ gates between each consecutive qubits pair
    CZ_INNER = "CZ_INNER"  # CZ gates between qubits in same register
    CY_INNER = "CY_INNER"  # CY gates between qubits in same register


MIXER_TYPES_DEFAULT = {
    TSPInput: [TSPMixerType.CY_CUSTOM, TSPMixerType.CZ],
    MVCInput: [],
    MHTInput: [],
    MhtQaoaInput: [],
}

for e in PROBLEM_INPUT_MAPPING.values():
    assert e in MIXER_TYPES_DEFAULT, "verify all problem inputs are accessible"
