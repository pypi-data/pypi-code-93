"""UNET preprocess."""
import numpy as np
from PIL import Image
from skimage.transform import resize

RESIZE_ROWS = 96
RESIZE_COLS = 96
TRAIN_MEAN = 98.814224
TRAIN_STD = 52.37462


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
    image = image.convert('L')  # converting to grayscale image
    image_array = np.asarray(image).astype(np.uint8)
    tensor = resize(image_array, (RESIZE_COLS, RESIZE_ROWS), preserve_range=True)
    tensor = np.expand_dims(tensor, axis=-1)

    tensor = tensor.astype('float32')
    tensor = tensor - TRAIN_MEAN
    tensor = tensor / TRAIN_STD

    assert tensor.shape == (RESIZE_ROWS, RESIZE_COLS, 1)
    assert tensor.dtype == np.float32

    return tensor


def image_mask_to_tensor(image: Image):
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
    image = image.convert('L')   # converting to grayscale image
    image_array = np.array(image, dtype=np.uint8)
    tensor = resize(image_array, (RESIZE_COLS, RESIZE_ROWS), preserve_range=True)
    tensor = np.expand_dims(tensor, axis=-1)

    tensor = tensor.astype('float32')
    tensor = tensor / 255.  # scale mask to [0,1] for consistency with Net's sigmoud output activation

    assert tensor.shape == (RESIZE_ROWS, RESIZE_COLS, 1)
    assert tensor.dtype == np.float32

    return tensor
