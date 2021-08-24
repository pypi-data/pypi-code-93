"""Utils for mnist dataset."""
import os
import glob

import cv2
import numpy as np


def save_calibration_tensor(path_to_dataset: str, save_dir: str):
    """
    Save JPEG images from dataset directory to calibration_tensors numpy file.

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
    for img in images:
        image = cv2.imread(img, 0)
        image = image / 255.0
        tensors.append(image)
    tensors = np.array(tensors, dtype='float32')
    tensors = np.expand_dims(tensors, -1)
    np.save(os.path.join(save_dir, 'calibration_tensors_mnist'), tensors)
