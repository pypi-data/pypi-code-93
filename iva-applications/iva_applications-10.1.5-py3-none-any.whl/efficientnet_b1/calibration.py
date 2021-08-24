"""Utils for efficientnet_b1 preprocessing from keras-applications."""
import os
import glob
import numpy as np
from PIL import Image
from iva_applications.efficientnet_b1.preprocess import image_to_tensor


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
    images = glob.glob(os.path.join(path_to_dataset, "*.JPEG"))
    for image in images:
        image = Image.open(image)
        tensor = image_to_tensor(image)
        tensors.append(tensor)
    tensors = np.array(tensors, dtype='float32')
    np.save(os.path.join(save_dir, 'calibration_tensors_efficientnet_b1'), tensors)
