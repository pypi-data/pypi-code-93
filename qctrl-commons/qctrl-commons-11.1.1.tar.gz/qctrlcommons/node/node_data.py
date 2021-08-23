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

"""
Module for inherited wrapper class.
"""

from dataclasses import (
    dataclass,
    field,
)
from typing import (
    Callable,
    List,
    Tuple,
)

import numpy as np

from qctrlcommons.node.wrapper import (
    NamedNodeData,
    NodeData,
)


class ArithmeticMixin:
    """
    Mixin to be used by NodeData that support binary arithmetic operations with
    number/array/Tensor/Pwc/Stf objects.

    By default ``arr + graph.op()`` throws an error, since NumPy doesn't know how to add
    `graph.op()` objects to arrays. Even the fact that the func ops override `__radd__` doesn't
    help, since the NumPy addition takes precedence. We can instead tell NumPy to delegate all
    binary operations to the other operand, by explicitly clearing the `__array_ufunc__`
    attribute.
    """

    __array_ufunc__ = None

    def __add__(self, other):
        return self.operation.graph.add(self, other)

    def __radd__(self, other):
        return self.operation.graph.add(other, self)

    def __sub__(self, other):
        return self.operation.graph.subtract(self, other)

    def __rsub__(self, other):
        return self.operation.graph.subtract(other, self)

    def __matmul__(self, other):
        return self.operation.graph.matmul(self, other)

    def __rmatmul__(self, other):
        return self.operation.graph.matmul(other, self)

    def __mul__(self, other):
        return self.operation.graph.multiply(self, other)

    def __rmul__(self, other):
        return self.operation.graph.multiply(other, self)

    def __floordiv__(self, other):
        return self.operation.graph.floordiv(self, other)

    def __rfloordiv__(self, other):
        return self.operation.graph.floordiv(other, self)

    def __pow__(self, power):
        return self.operation.graph.pow(self, power)

    def __rpow__(self, other):
        return self.operation.graph.pow(other, self)

    def __truediv__(self, other):
        return self.operation.graph.truediv(self, other)

    def __rtruediv__(self, other):
        return self.operation.graph.truediv(other, self)

    def __abs__(self):
        return self.operation.graph.abs(self)

    def __neg__(self):
        return self.operation.graph.negative(self)


@dataclass
class TensorNodeData(NamedNodeData, ArithmeticMixin):
    """
    Wrapper class for tensor type Node.
    """

    shape: Tuple[int]

    def __getitem__(self, item) -> "Operation":
        """
        refer to item in operation.

        Returns
        -------
        Operation
            getitem operation.
        """
        node_data = self.operation.graph.getitem(self, item)
        shape = np.empty(self.shape)[item].shape
        return TensorNodeData(node_data.operation, shape=shape)

    def __iter__(self):
        # Disable iteration for now. Even though this should work fine in theory (since all client
        # tensors have fully-defined shapes), allowing iterability on the client causes tensors to
        # pass checks that will fail in the backend (for example, if tensors are iterable on the
        # client, a multi-dimensional tensor can be passed to a function that expects a list of
        # tensors; such an input will fail in the backend though). This could be revisited in the
        # future if we're more strict about client-side validation of iterable inputs, or if we
        # update the backend to be able to iterate over tensors.
        raise TypeError(
            "You cannot iterate over Tensors directly. Instead you can iterate over the indices "
            "and extract elements of the tensor using `tensor[index]`."
        )

    def __repr__(self):
        return (
            f'<TensorNode: name="{self.name}", '
            f'operation_name="{self.operation.operation_name}", '
            f"shape={self.shape}>"
        )


@dataclass
class PwcNodeData(NamedNodeData, ArithmeticMixin):
    """
    Wrapper class for Pwc type Node.
    """

    value_shape: Tuple[int]
    durations: np.ndarray
    batch_shape: Tuple[int]

    @property
    def values(self):
        """
        Access to the values in Pwc.
        """
        node_data = self.operation.graph.getattr(self, "values")
        shape = (
            tuple(self.batch_shape) + (len(self.durations),) + tuple(self.value_shape)
        )
        return TensorNodeData(node_data.operation, shape=shape)

    def __repr__(self):
        return (
            f'<PwcNode: name="{self.name}", '
            f'operation_name="{self.operation.operation_name}", '
            f"value_shape={self.value_shape}, batch_shape={self.batch_shape}>"
        )


@dataclass
class StfNodeData(NodeData, ArithmeticMixin):
    """
    Wrapper class for Stf type Node.
    """

    value_shape: Tuple[int]
    batch_shape: Tuple[int]

    def __repr__(self):
        return (
            f'<StfNode: operation_name="{self.operation.operation_name}", '
            f"value_shape={self.value_shape}, batch_shape={self.batch_shape}>"
        )


@dataclass
class SparsePwcNodeData(NodeData):
    """
    Wrapper class for SparsePwc type Node.
    """

    value_shape: Tuple[int]

    def __repr__(self):
        return (
            f'<SparsePwcNode: operation_name="{self.operation.operation_name}", '
            f"value_shape={self.value_shape}>"
        )


@dataclass
class TargetNodeData(NodeData):
    """
    Wrapper class for Target type node.
    """

    value_shape: Tuple[int]

    def __repr__(self):
        return (
            f'<TargetNode: operation_name="{self.operation.operation_name}", '
            f"value_shape={self.value_shape}>"
        )


@dataclass
class SequenceNodeData(NamedNodeData):
    """
    Wrapper class for creating a sequence of Nodes.
    """

    items: List = field(default_factory=list)

    def create_sequence(
        self, node_constructor: Callable, size: int
    ) -> "SequenceNodeData":
        """
        Populates the `items` of the sequence from the operation.

        Parameters
        ----------
        node_constructor : Callable
            A callable to generate the node data for the sequence.
        size : int
            Size of the sequence.

        Returns
        -------
        SequenceNodeData
            The sequence itself.
        """

        get_item_op = lambda item: self.operation.graph.getitem(self, item).operation

        self.items = [
            node_constructor(get_item_op(index), index) for index in range(size)
        ]

        return self

    def __getitem__(self, index) -> "Operation":
        return self.items[index]

    def __iter__(self):
        return iter(self.items)

    def __len__(self):
        return len(self.items)

    def __repr__(self):
        return (
            f'<SequenceNodeData: operation_name="{self.operation.operation_name}", '
            f"items={self.items}>"
        )
