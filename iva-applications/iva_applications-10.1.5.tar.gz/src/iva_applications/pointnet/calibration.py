"""Utils for pointnet preprocessing."""
import os
import glob
import numpy as np


def save_calibration_tensor(path_to_dataset: str, save_dir: str):
    """
    Save txt from dataset directory to calibration_tensors numpy file.

    Parameters
    ----------
    path_to_dataset
        Path to dataset directory
    save_dir
        Path to saving directory

    -------

    """
    tensors = []
    objects = glob.glob(os.path.join(path_to_dataset, "*.txt"))
    for obj in objects:
        obj = np.loadtxt(obj)
        obj = np.reshape(obj, (1, 2048, 3))
        tensors.append(obj)
    tensors = np.array(tensors, dtype='float32')
    np.save(os.path.join(save_dir, 'calibration_tensors_modelnet40'), tensors)
