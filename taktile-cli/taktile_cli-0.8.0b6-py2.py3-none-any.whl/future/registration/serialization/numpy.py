import json

import numpy as np

from tktl.future.utils import JSONStructure


def numpy_deserialize(*, value: JSONStructure, sample: np.ndarray) -> np.ndarray:
    return np.array(value)


def numpy_serialize(*, value: np.ndarray) -> JSONStructure:
    return value.tolist()


def numpy_to_example(*, value: np.ndarray) -> str:
    return json.dumps(value[0:1].tolist())
