# -*- coding=utf-8 -*-
"""YOLO2 preprocess."""
import numpy as np
from PIL import Image


def image_to_tensor(image: Image, yolo_size: int = 608) -> np.ndarray:
    """
    Realise preprocess for an input pillow image and convert it to numpy array.

    Parameters
    ----------
    image
        An input image to be processed.
    yolo_size
        Shape of the input tensor

    Returns
    -------
    tensor
        Preprocessed numpy array.
    """
    image = image.resize((yolo_size, yolo_size), Image.BICUBIC)
    image = image.convert('RGB')
    tensor = np.asarray(image).astype(np.float32)
    tensor = tensor / 255.0
    assert tensor.shape == (yolo_size, yolo_size, 3)
    return tensor
