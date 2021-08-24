# -*- coding=utf-8 -*-
"""RESNET34 preprocess."""
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
    tensor = crop_and_resize(tensor, 224)
    tensor = tensor.astype(np.float32)
    # batch normalization values
    tensor *= np.array([[0.014244, 0.01466, 0.01409]])
    tensor += np.array([-1.254, -1.281, -1.305])
    assert tensor.shape == (224, 224, 3)
    return tensor
