# -*- coding=utf-8 -*-
"""SQUEEZENET preprocess."""
import numpy as np
from PIL import Image
from iva_applications.imagenet.images_utils import crop_and_resize


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
    mean = [103.939, 116.779, 123.68]
    image = image.convert('RGB')
    tensor = np.asarray(image)
    tensor = crop_and_resize(tensor, 227)
    tensor = tensor[..., ::-1]
    tensor = tensor - np.array(mean)
    tensor = tensor.astype(np.float32)
    assert tensor.shape == (227, 227, 3)
    return tensor
