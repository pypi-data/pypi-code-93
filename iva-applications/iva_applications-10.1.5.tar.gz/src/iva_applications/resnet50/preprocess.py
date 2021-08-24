# -*- coding=utf-8 -*-
"""RESNET50 preprocess."""
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
    mean = [123.68, 116.779, 103.939]
    image = image.convert('RGB')
    tensor = np.asarray(image)
    tensor = crop_and_resize(tensor, 224)
    tensor = tensor - np.array(mean)
    tensor = tensor.astype(np.float32)
    assert tensor.shape == (224, 224, 3)
    return tensor
