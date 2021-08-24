# -*- coding=utf-8 -*-
"""Lenet preprocess."""
import numpy as np


def tpu_tensor_to_classes(tensor: np.ndarray, top: int = 1) -> np.ndarray:
    """
    Realise postprocess of tensor for Mnist based networks and convert it to numpy array.

    Parameters
    ----------
    tensor
        Inference result.
    top
        Number of values to return.

    Returns
    -------
        Inference result decoded to classes.
    """
    num_classes = tensor.flatten().argsort()[::-1][:top]
    return num_classes
