import dataclasses

from datetime import datetime

from aide_sdk.model.resource import Resource


@dataclasses.dataclass
class Origin(Resource):
    received_timestamp: datetime
    patient_id: str
