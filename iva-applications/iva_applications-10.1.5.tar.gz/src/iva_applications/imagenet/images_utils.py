"""Images utils."""
import cv2
import numpy as np


def central_crop(image, percent=1.):
    """Crop center from image."""
    height, width = np.shape(image)[:2]
    min_dim = int(min(height, width) * percent)
    crop_top = (height - min_dim) // 2
    crop_left = (width - min_dim) // 2
    return image[crop_top:crop_top + min_dim, crop_left:crop_left + min_dim]


def crop_and_resize(img_data, new_img_size):
    """Crop center from image and resize it to another shape."""
    new_img = central_crop(img_data, 0.85)
    new_img = cv2.resize(new_img, (new_img_size, new_img_size))
    return new_img
