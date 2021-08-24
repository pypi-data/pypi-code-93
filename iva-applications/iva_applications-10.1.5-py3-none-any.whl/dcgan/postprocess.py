"""Postprocessing functions for DCGAN."""
import numpy as np
from PIL import Image


def save_fig(rows: int, columns: int, output: np.ndarray, save_path: str):
    """
    Save the generated image with random numbers.

    Parameters
    ----------
    rows
        Number of rows of numbers
    columns
        Number of columns of numbers
    output
        The output of the generator
    save_path
        The path to save the generated image

    Returns
    -------
    None
    """
    shape = output.shape
    result_image = Image.new('L', (shape[1] * columns, shape[2] * rows))
    ind = 0
    for row in range(rows):
        for col in range(columns):
            single_array = np.squeeze(output[ind])
            scaled_array = (single_array * 255.0).astype(np.uint8)
            image = Image.fromarray(scaled_array, 'L')
            result_image.paste(image, (col * image.width, row * image.height))
            ind = ind + 1
    result_image.save(save_path, 'PNG')
