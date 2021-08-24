# -*- coding=utf-8 -*-
"""COVIDNet preprocess."""
import numpy as np
from PIL import Image
import cv2


def image_to_tensor(image: Image) -> np.ndarray:
    """
    Preprocess for COVIDNet.

    Parameters
    ----------
    imgage
        image in form of a PIL object
    Returns
    -------
    tensor
        Preprocessed numpy array.
    """
    image = image.convert('RGB')
    img = np.asarray(image)
    percent = .08
    offset = int(img.shape[0] * percent)
    img = img[offset:]
    size = min(img.shape[0], img.shape[1])
    offset_h = int((img.shape[0] - size) / 2)
    offset_w = int((img.shape[1] - size) / 2)
    img = img[offset_h:offset_h + size, offset_w:offset_w + size]
    img = cv2.resize(img, (480, 480))
    img = img.astype('float32') / 255.
    return img
