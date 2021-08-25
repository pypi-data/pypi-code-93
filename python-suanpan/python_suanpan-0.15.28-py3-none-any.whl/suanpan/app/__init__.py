# coding=utf-8
from __future__ import absolute_import, print_function

from suanpan import g
from suanpan.proxy import Proxy


class App(Proxy):
    MAPPING = {
        "spark": "suanpan.app.spark.SparkApp",
        "docker": "suanpan.app.docker.DockerApp",
        "stream": "suanpan.app.stream.StreamApp",
    }

    @property
    def isSpark(self):
        return self.isType("spark")

    @property
    def isDocker(self):
        return self.isType("docker")

    @property
    def isStream(self):
        return self.isType("stream")

    def isType(self, appType):
        return getattr(self, self.TYPE_KEY, None) == appType


TYPE = g.appType
app = App(type=TYPE)
