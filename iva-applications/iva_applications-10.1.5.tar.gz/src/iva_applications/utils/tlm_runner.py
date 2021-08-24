"""Runner to run on TLM."""
import logging
import pickle
from typing import Dict
from typing import Set
from typing import TYPE_CHECKING

import numpy as np

from .helpers import add_zero_suffix
from .helpers import op_to_tensor
from .helpers import strip_zero_suffix
from .helpers import tensor_to_op
from .runner import Runner

if TYPE_CHECKING:
    from tpu_tlm_is import Executable
    from tpu_tlm_is.base import TensorDescription

__all__ = [
    'TLMRunner'
]

LOGGER = logging.getLogger(__name__)


class _ProxyRunner:
    """In-memory proxy runner class that does not force us to use filesystem to store objects."""

    def __init__(self, executable: 'Executable', tensor_descriptions: Dict[str, 'TensorDescription']):
        self._executable = executable
        self._tensor_descriptions = tensor_descriptions

    @property
    def in_tensors(self) -> Set[str]:
        """Set of input tensor names."""
        return {add_zero_suffix(i) for _, j in self._executable.in_data.items() for i in j}

    @property
    def out_tensors(self) -> Set[str]:
        """Set of output tensor names."""
        return {add_zero_suffix(i) for _, j in self._executable.out_data.items() for i in j}

    def _check_input_names(self, input_tensors: Dict[str, np.ndarray]):
        if input_tensors.keys() != self.in_tensors:
            raise ValueError(f'Expected inputs {self.in_tensors}'
                             f' differs from the provided {input_tensors.keys()}')

    def _check_input_shapes(self, input_tensors: Dict[str, np.ndarray]):
        for name, tensor in input_tensors.items():
            expected_shape = self._tensor_descriptions[strip_zero_suffix(name)].user_shape.nhwc
            if tensor.shape != expected_shape:
                raise ValueError(f'Invalid input shape {tensor.shape} for tensor "{name}": expected {expected_shape}')

    def __call__(self, input_tensors: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        # pylint: disable=import-outside-toplevel
        from tpu_compiler_frontend import tlm
        self._check_input_names(input_tensors)
        self._check_input_shapes(input_tensors)
        input_tensors = tensor_to_op(input_tensors)
        _, output_tensors = tlm((self._executable, self._tensor_descriptions), input_tensors)
        return op_to_tensor(output_tensors)


# NOTE: TLMRunner class is therefore follows the pattern of a humble object.

class TLMRunner(Runner):
    """TLM runner."""

    def __init__(self, tlm_program_path: str):
        # pylint: disable=import-outside-toplevel
        from tpu_tlm_is import Executable
        from tpu_tlm_is.base import TensorDescription

        executable: Executable
        tensor_descriptions: Dict[str, TensorDescription]

        with open(tlm_program_path, 'rb') as file:
            executable, tensor_descriptions = pickle.load(file)

        self._proxy = _ProxyRunner(executable, tensor_descriptions)

        # TODO: the following initialization if only to comly with Runner base and
        #  is not needed by the TLM runner itself. It is also wrong to convert from set to list
        #  but the base classes forces us to provide a list.
        super().__init__(source_path=tlm_program_path,
                         input_nodes=list(self._proxy.in_tensors),
                         output_nodes=list(self._proxy.out_tensors))

    def __call__(self, input_tensors: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """Perform TLM run for a given input."""
        return self._proxy(input_tensors)
