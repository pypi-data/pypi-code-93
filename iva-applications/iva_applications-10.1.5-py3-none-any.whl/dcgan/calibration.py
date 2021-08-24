"""Utils for DCGAN."""
import os
import numpy as np


def save_calibration_tensor(save_dir: str, number_of_calibration_images: int = 100, latent_dim: int = 100):
    """
    Save numpy normal noise as calibration_tensors numpy file.

    Parameters
    ----------
    save_dir
        Path to saving directory.
    number_of_calibration_images
        Number of generated calibration images.
    latent_dim
        Latency parameter.

    -------

    """
    tensors = np.random.normal(0, 1, (number_of_calibration_images, latent_dim))
    np.save(os.path.join(save_dir, 'calibration_tensors_dcgan'), tensors)
