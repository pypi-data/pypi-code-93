# -*- coding=utf-8 -*-
"""Inceptionv4 preprocess."""
import numpy as np
from PIL import Image
from iva_applications.imagenet.images_utils import crop_and_resize


def image_to_tensor(image: Image) -> np.ndarray:
    """Convert pillow image to tensor."""
    image = image.convert('RGB')
    tensor = np.asarray(image)
    tensor = crop_and_resize(tensor, 299)
    tensor = (tensor / 255.0 - 0.5) * 2.0
    assert tensor.shape == (299, 299, 3)
    return tensor
