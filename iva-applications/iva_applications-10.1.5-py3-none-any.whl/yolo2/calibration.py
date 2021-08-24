"""Utils for coco dataset."""
import os
import glob

import cv2
import numpy as np


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
    tensor = []
    images = glob.glob(os.path.join(path_to_dataset, "*.jpg"))
    for img in images:
        image = cv2.imread(img)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, (608, 608))
        image = image / 255.0
        tensor.append(image)
    tensor = np.array(tensor, dtype='float32')
    np.save(os.path.join(save_dir, 'calibration_tensors_coco2017'), tensor)
