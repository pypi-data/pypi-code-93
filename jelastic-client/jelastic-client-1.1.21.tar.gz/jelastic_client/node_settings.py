from typing import NamedTuple


class DockerSettings(NamedTuple):
    image: str
    nodeGroup: str = None


class NodeSettings(NamedTuple):
    docker: DockerSettings = None
    count: int = 1
    displayName: str = None
    extip: bool = False
    fixedCloudlets: int = None
    flexibleCloudlets: int = None
    nodeType: str = None


MultipleNodeSettings = list[NodeSettings]
