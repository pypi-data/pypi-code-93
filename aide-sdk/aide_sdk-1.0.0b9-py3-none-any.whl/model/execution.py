import dataclasses
import uuid


@dataclasses.dataclass
class Execution:
    model_uid: str
    execution_uid: uuid.UUID
