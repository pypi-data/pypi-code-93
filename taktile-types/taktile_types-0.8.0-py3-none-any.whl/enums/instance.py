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


class InstanceType(ExtendedEnum):
    """Instance types of Taktile Deployments.

    * GP: general purpose (deprecated)
    * GPU: deployment with a GPU attached
    * CPU: deployment with 1 cpu but varying RAM sizes
    """

    GP = "gp"
    GPU = "gpu"
    CPU = "cpu"


class ServiceType(ExtendedEnum):
    """Enum for service types."""

    REST = "rest"
    GRPC = "grpc"
