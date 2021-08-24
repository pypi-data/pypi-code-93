"""Abstract base for various runners."""

from abc import ABC, abstractmethod
from typing import List, Dict

import numpy as np


class Runner(ABC):
    """Abstract parent class for Runners."""

    def __init__(
            self,
            source_path: str,
            input_nodes: List[str],
            output_nodes: List[str]):
        """Initialize Runner."""
        self._source_path = source_path
        self._input_nodes = input_nodes
        self._output_nodes = output_nodes

    @property
    def source_path(self):
        """Path to program of tensorflow graph."""
        return self._source_path

    @property
    def input_nodes(self):
        """Input nodes names."""
        return self._input_nodes

    @property
    def output_nodes(self):
        """Output nodes names."""
        return self._output_nodes

    @abstractmethod
    def __call__(self, tensor: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """Abstract inference."""
        ...
