"""Utils for inception_v3."""
import os
import glob
import numpy as np
from PIL import Image
from iva_applications.inception_v4.preprocess import image_to_tensor


def save_calibration_tensor(path_to_dataset: str, save_dir: str):
    """Save tensor for calibration."""
    tensors = []
    images = glob.glob(os.path.join(path_to_dataset, "*.JPEG"))
    for image in images[:100]:
        image = Image.open(image)
        tensor = image_to_tensor(image)
        tensors.append(tensor)
    tensors = np.array(tensors, dtype='float32')
    np.save(os.path.join(save_dir, 'calibration_tensors_inception_v4'), tensors)
