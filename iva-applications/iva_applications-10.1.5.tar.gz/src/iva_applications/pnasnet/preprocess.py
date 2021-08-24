# -*- coding=utf-8 -*-
"""pnasnet preprocess."""
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
    image = image.convert('RGB')
    tensor = np.asarray(image)
    tensor = crop_and_resize(tensor, 331)
    tensor = (tensor / 255.0 - 0.5) * 2.0
    tensor = tensor.astype(np.float32)
    assert tensor.shape == (331, 331, 3)
    return tensor
