"""Utils for CCOVIDx dataset."""
import os
import glob
import numpy as np
from PIL import Image
from iva_applications.covidnet_cxr4_a.preprocess import image_to_tensor


def save_calibration_tensor(path_to_dataset: str, save_dir: str) -> None:
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
    images = glob.glob(os.path.join(path_to_dataset, "*"))
    images = np.random.choice(images, size=100)
    for image in images:
        img = Image.open(image).convert('RGB')
        img = image_to_tensor(img)
        tensors.append(img)
    tensors = np.array(tensors, dtype='float32')
    np.save(os.path.join(save_dir, 'calibration_tensors_covidnet'), tensors)
