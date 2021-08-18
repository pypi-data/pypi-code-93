import os
from enum import Enum
from typing import Dict


class Environment(str, Enum):
    NAIS: str = "nais"
    GCS: str = "gcs"


def configure_environment(datapackage: Dict):
    datapackage["environment"] = os.getenv("DATAVERK_ENVIRONMENT")
    datapackage["path"] = f"/api/{datapackage['id']}"
