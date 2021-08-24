"""MOBILE FACE NET preprocess."""
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
    image = image.resize((112, 112), Image.BICUBIC)
    image = image.convert('RGB')
    tensor = np.asarray(image).astype(np.float32)
    tensor = (tensor - 127.5) * 0.0078125
    assert tensor.shape == (112, 112, 3)
    return tensor
