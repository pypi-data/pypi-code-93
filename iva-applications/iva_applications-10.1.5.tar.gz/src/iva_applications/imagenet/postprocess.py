# -*- coding=utf-8 -*-
"""Imagenet dataset postprocessing."""
import numpy as np
from iva_applications.imagenet.config import CLASS_DICT


def softmax(tensor) -> np.ndarray:
    """Compute softmax values for each sets of scores in x."""
    e_x = np.exp(tensor - np.max(tensor))
    return e_x / e_x.sum(axis=0)


def tpu_tensor_to_num_classes(tensor: np.ndarray, top: int = 1) -> np.ndarray:
    """Get top N classes of output tensor."""
    tensor = np.reshape(tensor, (tensor.shape[0], tensor.shape[-1]))
    num_classes = np.squeeze(tensor.argsort()[::, -top:])[()]
    # the operation '[()]' returns number if the array in 0-d and returns an array otherwise
    if not isinstance(num_classes, np.ndarray):
        num_classes = np.array([num_classes])
    return num_classes


def decode_classes(num_classes: np.ndarray) -> list:
    """Decode class numbers to class names."""
    names = []
    for value in num_classes:
        names.append(CLASS_DICT[value])
    return names


def tpu_tensor_to_classes(tensor: np.ndarray, top: int = 1) -> list:
    """Decode tpu tensor to classes."""
    return decode_classes(tpu_tensor_to_num_classes(tensor, top))
