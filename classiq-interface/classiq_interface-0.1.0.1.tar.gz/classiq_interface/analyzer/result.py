from enum import Enum
from typing import Union, Set, List, Optional

from pydantic import BaseModel, Field, conint

Match = List[List[int]]


class AnalysisStatus(str, Enum):
    NONE = "none"
    SUCCESS = "success"
    CANCELLED = "cancelled"
    ERROR = "error"


class BasisGates(str, Enum):
    CX = "cx"
    CY = "cy"
    CZ = "cz"
    U = "u"
    U2 = "u2"
    P = "p"


class QuantumCircuitProperties(BaseModel):
    depth: conint(ge=0) = Field(default=..., description="Circuit depth")
    auxiliary_qubits: conint(ge=0) = Field(
        default=..., description="Number of Auxiliary qubits"
    )
    classical_bits: conint(ge=0) = Field(
        default=..., description="Number of classical bits"
    )
    gates_count: conint(ge=0) = Field(
        default=..., description="Total number of gates in the circuit"
    )
    multi_qubit_gates_count: conint(ge=0) = Field(
        default=..., description="Number of multi-qubit gates in circuit"
    )
    non_entangled_subcircuits_count: conint(ge=0) = Field(
        default=..., description="Number of non-entangled sub-circuit "
    )


class NativeQuantumCircuitProperties(QuantumCircuitProperties):
    native_gates: Set[BasisGates] = Field(
        default=..., description="Native gates used for decomposition"
    )


class PatternRecognitionResult(BaseModel):
    found_patterns: List[str]


class PatternMatchingResult(BaseModel):
    found_patterns: List[str]


class Circuit(BaseModel):
    closed_circuit_qasm: str
    image: str


class PatternAnalysis(BaseModel):
    pattern_matching: Optional[PatternMatchingResult] = Field(
        default=..., description="Pattern matching algorithm"
    )
    pattern_recognition: Optional[PatternRecognitionResult] = Field(
        default=..., description="Find unknown patterns"
    )
    circuit: Circuit = Field(
        default=..., description="Quantum circuit after pattern analysis"
    )


class Analysis(BaseModel):
    input_properties: QuantumCircuitProperties = Field(
        default=..., description="Input circuit properties"
    )
    native_properties: NativeQuantumCircuitProperties = Field(
        default=..., description="Transpiled circuit properties"
    )
    pattern_analysis: Optional[PatternAnalysis] = Field(
        default=None,
        description="Pattern analysis, including pattern matching and pattern recognition",
    )


class AnalysisResult(BaseModel):
    status: AnalysisStatus
    details: Union[Analysis, str]
