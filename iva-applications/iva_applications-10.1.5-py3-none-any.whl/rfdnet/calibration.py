"""Utils for rfdnet."""
import os
import glob
import random
import numpy as np
from PIL import Image
from iva_applications.rfdnet.preprocess import image_to_tensor


def save_calibration_tensor(path_to_dataset: str, save_dir: str):
    """
    Save png images from dataset directory to calibration_tensors numpy file.

    Parameters
    ----------
    path_to_dataset
        Path to dataset directory.
    save_dir
        Path to saving directory.
    """
    tensors = []
    images_path = glob.glob(os.path.join(path_to_dataset, "*.png"))
    random.shuffle(images_path)
    for image_path in images_path:
        image = Image.open(image_path)
        image = image.resize((512, 512), Image.BICUBIC)
        tensor = image_to_tensor(image)
        tensors.append(tensor)
    tensors = np.array(tensors)
    np.save(os.path.join(save_dir, 'calibration_tensors_div2k_x3'), tensors)
    loaded_tensors = np.load(os.path.join(save_dir, 'calibration_tensors_div2k_x3.npy'))
    assert np.allclose(tensors, loaded_tensors)
