from typing import NamedTuple, List


class DockerSettings(NamedTuple):
    image: str
    nodeGroup: str = None


class EnvNode(NamedTuple):
    docker: DockerSettings = None
    count: int = 1
    displayName: str = None
    extip: bool = False
    fixedCloudlets: int = 1
    flexibleCloudlets: int = 1
    nodeType: str = None


EnvNodes = List[EnvNode]
