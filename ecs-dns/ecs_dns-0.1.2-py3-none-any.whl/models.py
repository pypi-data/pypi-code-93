"""Data models for ECS CNAME."""

from dataclasses import dataclass
from typing import Dict, List


@dataclass(order=True)
class ECSNetworkMetadata:
    """ECS container network metadata."""

    NetworkMode: str
    IPv4Addresses: List[str]


@dataclass(order=True)
class ECSContainerMetadata:
    """ECS container metadata."""

    DockerId: str
    Name: str
    DockerName: str
    Image: str
    ImageID: str
    Labels: Dict[str, str]
    DesiredStatus: str
    KnownStatus: str
    Limits: Dict[str, int]
    CreatedAt: str
    StartedAt: str
    Type: str
    Networks: List[ECSNetworkMetadata]

    def from_dict(source: Dict):
        source["Networks"] = [ECSNetworkMetadata(**c) for c in source["Networks"]]
        return ECSContainerMetadata(**source)


@dataclass(order=True)
class ECSTaskMetadata:
    """ECS task metadata response object."""

    Cluster: str
    TaskARN: str
    Family: str
    Revision: str
    DesiredStatus: str
    KnownStatus: str
    Containers: List[ECSContainerMetadata]
    PullStartedAt: str
    PullStoppedAt: str
    AvailabilityZone: str

    def from_dict(source: Dict):
        source["Containers"] = [
            ECSContainerMetadata.from_dict(c) for c in source["Containers"]
        ]
        return ECSTaskMetadata(**source)
