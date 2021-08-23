# Copyright 2021 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#      https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.
"""Module for custom Graph."""
import logging
from typing import (
    Callable,
    Dict,
    List,
)

from qctrlcommons.node.base import LOCAL_THREADING
from qctrlcommons.node.registry import NODE_REGISTRY

LOGGER = logging.getLogger(__name__)


class Graph:
    """
    Dataflow graph can extending custom node
    """

    def __init__(
        self, operations: Dict[str, str] = None, dependencies: List = None, name=None
    ):
        self.name = name or id(self)
        self.operations = operations or {}
        self.dependencies = dependencies or []

    def __enter__(self):
        assert (
            getattr(LOCAL_THREADING, "default_graph", None) is None
        ), "cannot have more than one default graph"
        LOCAL_THREADING.default_graph = self
        return self

    def __exit__(self, *args):
        assert LOCAL_THREADING.default_graph is self
        LOCAL_THREADING.default_graph = None

    def __getattr__(self, attr):
        # We override getattr to stop pylint from complaining about missing attributes for methods
        # that are added dynamically.
        raise AttributeError

    def __str__(self):
        return f"Q-CTRL Graph {self.name}"


def _extend_method(cls, func: Callable):
    """
    Extends the specified class by adding methods as attributes.

    Parameters
    ----------
    cls : class
        The class to which the function should be added.
    func : Callable
        Function to be added to the class as a method.
    """
    func_name = func.__name__
    if hasattr(cls, func_name):
        LOGGER.debug("existing attr %s on namespace: %s", func_name, cls)
    else:
        LOGGER.debug("adding attr %s to namespace: %s", func_name, cls)
        setattr(cls, func_name, func)


# set nodes to Graph
for node_cls in NODE_REGISTRY.as_list():
    node = node_cls.create_graph_method()
    _extend_method(Graph, node)
