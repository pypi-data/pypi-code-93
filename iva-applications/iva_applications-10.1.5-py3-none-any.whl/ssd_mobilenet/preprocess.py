# -*- coding=utf-8 -*-
"""Preprocessing functions for ssd-mobilenet."""
import numpy as np
import cv2
from PIL import Image


def image_to_tensor(image: Image) -> np.ndarray:
    """
    Realise preprocess for an input pillow image and convert it to numpy array.

    Parameters
    ----------
    image
        An input image to be processed.

    Returns
    -------
    np.ndarray tensor used by the network
    """
    image = image.convert('RGB')
    tensor = np.asarray(image)
    tensor = cv2.resize(tensor, (300, 300))
    tensor = (tensor / 255.0 - 0.5) * 2.0
    tensor = tensor.astype(np.float32)
    assert tensor.shape == (300, 300, 3)
    return tensor
