# Apply White or Black Background Mask

import os

import cv2
import numpy as np

from weedcv.weedcv import params


def apply_mask(img, mask, mask_color):
    """Apply white image mask to image, with bitwise AND operator bitwise NOT operator and ADD operator.
    Inputs:
    img        = RGB image data
    mask       = Binary mask image data
    mask_color = 'white' or 'black'
    Returns:
    masked_img = masked image data
    :param img: numpy.ndarray
    :param mask: numpy.ndarray
    :param mask_color: str
    :return masked_img: numpy.ndarray
    """

    params.device += 1

    if mask_color.upper() == "WHITE":
        color_val = 255
    elif mask_color.upper() == "BLACK":
        color_val = 0

    array_data = img.copy()

    # Mask the array
    array_data[np.where(mask == 0)] = color_val

    return array_data
