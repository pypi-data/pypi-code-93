"""rfdnet postprocess."""
import numpy as np
from PIL import Image


def tensor_to_image(tensor: np.ndarray) -> Image:
    """
    Realise postprocess for numpy array and convert it to an output pillow image.

    Parameters
    ----------
    tensor
        Numpy array to be processed.

    Returns
    -------
    image
        Postprocessed an output image.
    """
    tensor *= 255.0
    tensor = tensor.clip(0, 255)
    tensor = tensor.reshape((np.shape(tensor)[1], np.shape(tensor)[2], 3))
    image = Image.fromarray(np.uint8(tensor))
    return image
