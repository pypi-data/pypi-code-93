"""TPURunner class."""
import asyncio
from typing import Dict
from typing import List

import numpy as np
from iva_tpu import TPUDevice, TPUProgram, TPUProgramInfo, TPUInference

from .helpers import add_zero_suffix
from .helpers import op_to_tensor
from .helpers import tensor_to_op
from .runner import Runner

__all__ = [
    'TPURunner'
]


def _get_tensor_names(tpu_program: TPUProgram, metadata_key: str) -> List[str]:
    return [add_zero_suffix(n[1]["anchor"]) for d in tpu_program.metadata[metadata_key].values() for n in d]


class TPURunner(Runner):
    """Runner for IVA TPU."""

    def __init__(self, program_path: str, loop=None, sync=False):

        tpu_program = TPUProgram(program_path, TPUProgramInfo())

        super().__init__(
            program_path,
            _get_tensor_names(tpu_program, 'inputs'),
            _get_tensor_names(tpu_program, 'outputs'),
        )

        self._program = tpu_program
        self._sync = sync
        self._loop = loop if loop else asyncio.get_event_loop()
        self._device = TPUDevice()
        self._device.load_program(tpu_program)

    def __call__(self, tensors: Dict[str, np.ndarray], dtype=np.float32) -> Dict[str, np.ndarray]:
        """
        Run inference using IVA TPU.

        Parameters
        ----------
        tensors
            Input tensors for inference
        dtype
            The desired data-type for the returned data (np.float32 or np.int8)
            If not given, then the type will be determined as np.float32.

        Returns: Result after TPU
        -------

        """
        tensors = tensor_to_op(tensors)
        inference = TPUInference(self._program)
        inference.load_tensors_dict(tensors)

        if self._sync:
            self._device.load_inference_sync(inference)
        else:
            status_future = self._device.load_inference(inference)
            self._loop.run_until_complete(status_future)

        tpu_out_tensors = inference.get_tensors_dict()
        return op_to_tensor(tpu_out_tensors)
