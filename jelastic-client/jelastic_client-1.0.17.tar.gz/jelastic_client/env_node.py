from typing import NamedTuple, List


class DockerSettings(NamedTuple):
    image: str
    nodeGroup: str = None


class EnvNode(NamedTuple):
    docker: DockerSettings = None
    count: int = 1
    displayName: str = None
    extip: bool = False
    fixedCloudlets: int = None
    flexibleCloudlets: int = None
    nodeType: str = None


EnvNodes = List[EnvNode]
