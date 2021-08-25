"""Resource related datastructures"""
import re
import typing as t

from pydantic import BaseModel, validator

RESOURCE_REGEX = re.compile("^([+-]?[0-9.]+)([eEinumkKMGTP]*[-+]?[0-9]*)$")


class ResourceRequirement(BaseModel):
    """ResourceRequirement
    A data structure to hold the cpu, memory, and gpu requirements of a service
    """

    cpu: t.Optional[str] = None
    memory: t.Optional[str] = None
    gpu: str = "0"

    @validator("gpu")
    def gpu_validator(
        cls, val
    ):  # pylint: disable=no-self-use,no-self-argument
        """Validates gpu resource request"""
        num = int(val)
        if num < 0:
            raise ValueError("GPU request must be a positive integer")
        return val

    @validator("cpu")
    def cpu_validator(
        cls, val
    ):  # pylint: disable=no-self-use,no-self-argument
        """Validates cpu resource request"""
        if not RESOURCE_REGEX.match(val):
            raise ValueError(
                "CPU request must match regex:"
                " ^([+-]?[0-9.]+)([eEinumkKMGTP]*[-+]?[0-9]*)$"
            )
        return val

    @validator("memory")
    def memory_validator(
        cls, val
    ):  # pylint: disable=no-self-use,no-self-argument
        """Validates memory resource request"""
        if not RESOURCE_REGEX.match(val):
            raise ValueError(
                "Memory request must match regex:"
                " ^([+-]?[0-9.]+)([eEinumkKMGTP]*[-+]?[0-9]*)$"
            )
        return val


SIZE_MAP = {
    "gp": {
        "small": ResourceRequirement(cpu="500m", memory="512Mi", gpu="0"),
        "medium": ResourceRequirement(cpu="1000m", memory="1Gi", gpu="0"),
        "large": ResourceRequirement(cpu="2000m", memory="2Gi", gpu="0"),
        "xlarge": ResourceRequirement(cpu="2000m", memory="4Gi", gpu="0"),
        "xxlarge": ResourceRequirement(cpu="2000m", memory="8Gi", gpu="0"),
    },
    "cpu": {
        "small": ResourceRequirement(cpu="500m", memory="512Mi", gpu="0"),
        "medium": ResourceRequirement(cpu="1000m", memory="1Gi", gpu="0"),
        "large": ResourceRequirement(cpu="1000m", memory="2Gi", gpu="0"),
        "xlarge": ResourceRequirement(cpu="1000m", memory="3Gi", gpu="0"),
        "xxlarge": ResourceRequirement(cpu="1000m", memory="4Gi", gpu="0"),
        "xxxlarge": ResourceRequirement(cpu="1000m", memory="8Gi", gpu="0"),
    },
    "gpu": {
        "small": ResourceRequirement(cpu="3500m", memory="14Gi", gpu="1"),
    },
}
