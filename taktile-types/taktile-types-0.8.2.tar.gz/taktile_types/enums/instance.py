"""Instance sizes and types."""
from .common import ExtendedEnum


class InstanceSize(ExtendedEnum):
    """The size values of instances."""

    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    XLARGE = "xlarge"
    XXLARGE = "xxlarge"
    XXXLARGE = "xxxlarge"


class InstanceClass(ExtendedEnum):
    """Instance classes of Taktile Deployments.

    * GP: general purpose (deprecated)
    * GPU: deployment with a GPU attached
    * CPU: deployment with 1 cpu but varying RAM sizes
    """

    GP = "gp"
    GPU = "gpu"
    CPU = "cpu"


class InstanceType(ExtendedEnum):
    """Valid instance types for Taktile Deployments"""

    GP_SMALL = "gp.small"
    GP_MEDIUM = "gp.medium"
    GP_LARGE = "gp.large"
    GP_XLARGE = "gp.xlarge"
    GP_2XLARGE = "gp.xxlarge"
    GPU_SMALL = "gpu.small"
    CPU_SMALL = "cpu.small"
    CPU_MEDIUM = "cpu.medium"
    CPU_LARGE = "cpu.large"
    CPU_XLARGE = "cpu.xlarge"
    CPU_2XLARGE = "cpu.xxlarge"
    CPU_3XLARGE = "cpu.xxxlarge"


class ServiceType(ExtendedEnum):
    """Enum for service types."""

    REST = "rest"
    GRPC = "grpc"
