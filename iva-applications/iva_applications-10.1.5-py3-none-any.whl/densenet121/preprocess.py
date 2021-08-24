# -*- coding=utf-8 -*-
"""Keras-applications 'torch' preprocess. suitable for densenet121, efficientnets, etc."""
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
        Preprocessed numpy array.
    """
    mean = [0.485, 0.456, 0.406]
    std = [0.229, 0.224, 0.225]
    image = image.convert('RGB')
    tensor = np.asarray(image)
    tensor = crop_and_resize(tensor, 224)
    tensor = tensor / 255.
    tensor[..., 0] -= mean[0]
    tensor[..., 1] -= mean[1]
    tensor[..., 2] -= mean[2]
    tensor[..., 0] /= std[0]
    tensor[..., 1] /= std[1]
    tensor[..., 2] /= std[2]
    tensor = tensor.astype(np.float32)
    assert tensor.shape == (224, 224, 3)
    return tensor
