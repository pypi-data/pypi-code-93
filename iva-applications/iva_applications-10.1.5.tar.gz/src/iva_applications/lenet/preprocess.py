# -*- coding=utf-8 -*-
"""LeNet preprocess."""
import numpy as np
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
    tensor
        Preprocessed numpy array.
    """
    image = image.resize((28, 28), Image.BICUBIC)
    tensor = np.asarray(image)
    tensor = np.expand_dims(tensor, axis=-1)
    tensor = tensor / 255.0
    tensor = tensor.astype(np.float32)
    assert tensor.shape == (28, 28, 1)
    return tensor
