"""Utils for UNET."""
import os
import glob
import numpy as np
from PIL import Image
from .preprocess import image_to_tensor


def save_calibration_tensor(path_to_dataset: str, save_dir: str):
    """
    Save tif from dataset directory to calibration_tensors numpy file.

    Parameters
    ----------
    path_to_dataset
        Path to dataset directory
    save_dir
        Path to saving directory

    -------

    """
    tensors = []
    image_names = glob.glob(os.path.join(path_to_dataset, '*.tif'))

    for image_name in image_names:
        if 'mask' in image_name:
            continue
        image = Image.open(image_name)
        tensor = image_to_tensor(image)
        tensors.append(tensor)

    tensors = np.array(tensors, dtype='float32')
    np.save(os.path.join(save_dir, 'calibration_tensors_unet'), tensors)
