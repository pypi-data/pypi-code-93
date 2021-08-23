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
Module for nodes related to optimization.
"""
from typing import (
    List,
    Optional,
    Sequence,
    Union,
)

import forge
import numpy as np

from qctrlcommons.exceptions import QctrlException
from qctrlcommons.node import types
from qctrlcommons.node.base import Node
from qctrlcommons.node.node_data import (
    SequenceNodeData,
    TensorNodeData,
)
from qctrlcommons.preconditions import (
    check_argument,
    check_argument_integer,
)


class OptimizationVariable(Node):
    r"""
    Creates optimization variables, which can be bounded, semi-bounded, or unbounded.

    Use this function to create a sequence of variables that can be tuned by
    the optimizer (within specified bounds) in order to minimize the cost
    function.

    Parameters
    ----------
    count : int
        The number :math:`N` of individual real-valued variables to create.
    lower_bound : float
        The lower bound :math:`v_\mathrm{min}` for generating an initial value for the variables.
        This will also be used as lower bound if the variables are lower bounded.
        The same lower bound applies to all `count` individual variables.
    upper_bound : float
        The upper bound :math:`v_\mathrm{max}` for generating an initial value for the variables.
        This will also be used as upper bound if the variables are upper bounded.
        The same upper bound applies to all `count` individual variables.
    is_lower_unbounded : bool, optional
        Defaults to False. Set this flag to `True` to define a semi-bounded variable with
        lower bound :math:`-\infty`; in this case, the `lower_bound` parameter is used only for
        generating an initial value.
    is_upper_unbounded : bool, optional
        Defaults to False. Set this flag to True to define a semi-bounded variable with
        upper bound :math:`+\infty`; in this case, the `upper_bound` parameter is used only for
        generating an initial value.
    name : str, optional
        The name of the node.

    Returns
    -------
    Tensor
        The sequence :math:`\{v_n\}` of :math:`N` optimization variables. If both
        `is_lower_unbounded` and `is_upper_unbounded` are `False`, these variables are
        bounded such that :math:`v_\mathrm{min}\leq v_n\leq v_\mathrm{max}`. If one of the
        flags is `True` (for example `is_lower_unbounded=True`), these variables are
        semi-bounded (for example :math:`-\infty \leq v_n \leq v_\mathrm{max}`).
        If both of them are `True`, then these variables are unbounded and satisfy that
        :math:`-\infty \leq v_n \leq +\infty`.

    See Also
    --------
    anchored_difference_bounded_variables : Create anchored optimization variables
        with a difference bound.
    :func:`~qctrl.dynamic.namespaces.FunctionNamespace.calculate_optimization` : Find the minimum
        of a generic function.
    """

    name = "optimization_variable"
    optimizable_variable = True
    args = [
        forge.arg("count", type=int),
        forge.arg("lower_bound", type=float),
        forge.arg("upper_bound", type=float),
        forge.arg("is_lower_unbounded", type=bool, default=False),
        forge.arg("is_upper_unbounded", type=bool, default=False),
    ]
    rtype = types.Tensor

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        count = kwargs["count"]
        lower_bound = kwargs["lower_bound"]
        upper_bound = kwargs["upper_bound"]
        if count <= 0:
            raise QctrlException(f"count={count} must be positive.")
        if upper_bound <= lower_bound:
            raise QctrlException(
                f"lower_bound={lower_bound} must be less than upper_bound={upper_bound}."
            )
        return TensorNodeData(_operation, shape=(count,))


class RandomChoices(Node):
    r"""
    Creates random samples from the data that you provide.

    You can provide the data as a list and each element of that list represents one component
    of the full data. For example, considering a single variable linear regression problem
    that is described by the input :math:`x` and output :math:`y`, the data you provide would
    be :math:`[x, y]`. The first dimension of the data component in this list is the size of
    the data and therefore must be same for all components. However, all these components can
    have different value shapes, meaning the other dimensions can vary.

    This node effectively chooses a random batch of `sample_count` indices :math:`\{s_i\}`,
    and extracts the corresponding slices :math:`\{c[s_i]\}` of each data component.
    For example, in the case of linear regression, you can use this node to extract a random
    subset of your full data set.

    If this node is evaluated multiple times (for example during an optimization), it samples
    indices without replacement until all indices have been seen, at which point it starts sampling
    from the full set of indices again. You can therefore use this node to create minibatches that
    iterate over your data set in a series of epochs.

    Parameters
    ----------
    data : List[Union[np.ndarray, Tensor]]
        A list of data components. The first dimensions of the elements in this
        list denote the total amount of the data, and therefore must be the same.
    sample_count : int
        Number of samples in the returned batch.
    seed : int, optional
        Seed for random number generator. Defaults to ``None``. If set, it ensures the
        random samples are generated in a reproducible sequence.
    name : str, optional
        The name of the node.

    Returns
    -------
    Sequence[Tensor]
        A sequence representing a batch of random samples from `data`.
        You can access the elements of the sequence using integer indices.
        The number of elements of the sequence is the same as the size of `data`.
        Each element of the sequence has the length (along its first dimension)
        as defined by `sample_count`.

    See Also
    --------
    :func:`~qctrl.dynamic.namespaces.FunctionNamespace.calculate_stochastic_optimization` : Performs
        gradient-based stochastic optimization of generic real-valued functions.
    """

    name = "random_choices"
    args = [
        forge.arg("data", type=List[Union[np.ndarray, types.Tensor]]),
        forge.arg("sample_count", type=int),
        forge.arg("seed", type=Optional[int], default=None),
    ]
    rtype = Sequence[types.Tensor]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        data = kwargs.get("data")
        sample_count = kwargs.get("sample_count")
        seed = kwargs.get("seed")

        data_size = data[0].shape[0]
        check_argument(
            all((value.shape[0] == data_size for value in data)),
            "The first dimension of the elements in `data` must be the same.",
            arguments={"data": data},
        )
        check_argument(
            0 < sample_count <= data_size,
            "`sample_count` must be positive and not greater than the size of the "
            "data you provide.",
            arguments={"sample_count": sample_count},
            extras={"data size": data_size},
        )
        if seed is not None:
            check_argument_integer(seed, "seed")

        return_tensor_shapes = [(sample_count,) + value.shape[1:] for value in data]
        node_constructor = lambda operation, index: TensorNodeData(
            operation, return_tensor_shapes[index]
        )
        return SequenceNodeData(_operation).create_sequence(
            node_constructor, size=len(data)
        )
