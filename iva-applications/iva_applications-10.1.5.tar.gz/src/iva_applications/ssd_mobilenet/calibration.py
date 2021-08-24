"""Calibration for SSD MobileNet v1."""
import os
import glob

import random
import numpy as np
from PIL import Image
from iva_applications.ssd_mobilenet.preprocess import image_to_tensor


def save_calibration_tensor(path_to_dataset: str, save_dir: str):
    """
    Save jpg images from dataset directory to calibration_tensors numpy file.

    Parameters
    ----------
    path_to_dataset
        Path to dataset directory.
    save_dir
        Path to saving directory.

    -------

    """
    tensors = []
    images = glob.glob(os.path.join(path_to_dataset, "*.jpg"))
    random.shuffle(images)
    for img in images[:100]:
        image = Image.open(img)
        tensor = image_to_tensor(image)
        tensors.append(tensor)
    tensors = np.array(tensors, dtype='float32')
    np.save(os.path.join(save_dir, 'calibration_tensors_ssd_mobilenet_v1'), tensors)
