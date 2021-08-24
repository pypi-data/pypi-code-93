"""Postprocess utils for MobileFaceNet."""
import numpy as np


def mobilefacenet_postprocess(output: np.ndarray) -> np.ndarray:
    """Postprocessing function."""
    output_original = output
    output = np.power(output, 2)
    output = np.sum(output, axis=1)
    output = np.reshape(output, (output[:].shape[0], 1))
    output = np.maximum(output, [1.000000013351432e-10])
    output = 1. / np.sqrt(output)
    output = output * output_original

    return output
