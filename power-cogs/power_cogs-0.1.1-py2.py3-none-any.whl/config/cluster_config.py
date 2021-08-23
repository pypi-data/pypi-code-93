from typing import Optional

from pydantic.dataclasses import dataclass

# internal
from power_cogs.config import Config


@dataclass
class ClusterConfig(Config):
    name: str = ""
    cluster_config_path: Optional[str] = None
    join_cluster: bool = False


@dataclass
class LocalClusterConfig(ClusterConfig):
    pass
