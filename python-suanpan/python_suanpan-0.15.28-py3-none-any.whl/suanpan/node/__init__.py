# coding=utf-8
from __future__ import absolute_import, print_function

import os

from suanpan import app
from suanpan.proxy import Proxy


class Node(Proxy):
    MAPPING = {
        "spark": "suanpan.node.spark.SparkNode",
        "docker": "suanpan.node.docker.DockerNode",
        "stream": "suanpan.node.stream.StreamNode",
    }


node = Node(type=app.TYPE)
