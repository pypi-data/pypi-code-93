# -*- coding=utf-8 -*-
"""YOLO4 preprocess."""
from typing import Tuple

from PIL import Image
import numpy as np
import cv2


def image_to_tensor(image: Image, yolo_size: Tuple[int, int] = (608, 608)) -> np.ndarray:
    """
    Realise preprocess for an input image.

    Parameters
    ----------
    image
        An input PIL image to be processed.
    yolo_size
        Shape of the input tensor

    Returns
    -------
    tensor
        Preprocessed numpy array.
    """
    if not isinstance(image, (Image.Image)):
        raise TypeError(f'img should be {Image.Image} Image. Got {type(image)}')

    image = image.convert('RGB')
    image = np.asarray(image).astype(np.float32)
    yolo_h, yolo_w = yolo_size
    image_h, image_w, _ = image.shape

    scale = min(yolo_w/image_w, yolo_h/image_h)
    new_w, new_h = int(scale * image_w), int(scale * image_h)
    image_resized = cv2.resize(image, (new_w, new_h))

    image_paded = np.full(shape=[yolo_h, yolo_w, 3], fill_value=128.0)
    delta_w, delta_h = (yolo_w - new_w) // 2, (yolo_h-new_h) // 2
    image_paded[delta_h:new_h+delta_h, delta_w:new_w+delta_w, :] = image_resized
    image_paded = image_paded / 255.0
    assert image_paded.shape == (yolo_h, yolo_w, 3)

    return image_paded
