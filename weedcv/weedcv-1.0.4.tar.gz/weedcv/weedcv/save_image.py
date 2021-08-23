from pathlib import Path

import cv2
import numpy as np


def save_image(visual, filename):
    """
    Saves annotation results to a file for review
    """
    image_type = type(visual)
    if image_type == np.ndarray:
        cv2.imwrite(str(filename), visual)
