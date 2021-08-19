from dataclasses import dataclass


@dataclass
class DataResourceSchema:
    type: str
    name: str
    description: str
    fileFormat: str
