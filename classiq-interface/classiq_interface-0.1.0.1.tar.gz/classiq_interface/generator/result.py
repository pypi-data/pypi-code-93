import enum
from typing import Union, List, Optional

import pydantic

from classiq_interface.generator.generation_metadata import GenerationMetadata


class QuantumFormat(str, enum.Enum):
    QASM = "qasm"
    QSHARP = "qs"


class GenerationStatus(str, enum.Enum):
    NONE = "none"
    SUCCESS = "success"
    UNSAT = "unsat"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    ERROR = "error"


class GeneratedCircuit(pydantic.BaseModel):
    qasm: Optional[str]
    qsharp: Optional[str]
    output_format: List[QuantumFormat]
    image: str
    metadata: GenerationMetadata


class GenerationResult(pydantic.BaseModel):
    status: GenerationStatus
    details: Union[GeneratedCircuit, str]
