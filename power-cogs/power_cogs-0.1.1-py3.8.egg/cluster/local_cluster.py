import typing

import attr

from power_cogs.cluster.cluster import Cluster
from power_cogs.config.cluster_config import LocalClusterConfig
from power_cogs.config.config import class_config


@class_config(LocalClusterConfig)
@attr.s(repr=False)
class LocalCluster(Cluster):
    def setup(self):
        pass

    def shutdown(self):
        pass

    def execute(self, execution, *args, **kwargs):
        return [execution.execute(*args, **kwargs)]

    def put(self, obj, name):
        self.cache[name] = obj

    def get(self, name: str) -> typing.Any:
        return self.cache[name]
