"""rfdnet preprocess."""
import numpy as np
from PIL import Image


def image_to_tensor(image: Image) -> np.ndarray:
    """
    Realise preprocess for an input pillow image and convert it to numpy array.

    Parameters
    ----------
    image
        An input image to be processed.

    Returns
    -------
    tensor
        Preprocessed numpy array.
    """
    tensor = np.asarray(image)
    tensor = tensor / 255.0
    tensor = tensor.astype(np.float32)
    return tensor
