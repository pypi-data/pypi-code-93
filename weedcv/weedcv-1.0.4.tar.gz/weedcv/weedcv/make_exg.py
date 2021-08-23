from pathlib import Path

import cv2
import numpy as np

from weedcv.weedcv import params
from weedcv.weedcv._debug import _debug


def make_exg(rgb_img, exg_thresh=0):
    """
    Excess Green Index

    r = R / (R + G + B)
    g = G / (R + G + B)
    b = B / (R + G + B)

    EXG = 2 * G - R - B

    ExG values range from -1 to 2.

    Inputs:
    rgb_img      = np array in RGB

    Returns:
    index_array    = single channel np array (float32)
    """

    if rgb_img is None:
        raise RuntimeError("RGB image is None.")

    img = rgb_img.astype(float)

    blue = img[:, :, 2]
    green = img[:, :, 1]
    red = img[:, :, 0]

    exg = (2 * green) - red - blue

    # Thresholding removes low negative values
    exg = np.where(exg < exg_thresh, 0, exg).astype("uint8")

    _debug(
        exg,
        filename=Path(
            params.debug_outdir,
            str(params.debug_filename) + "_" + str(params.device) + "_exg.PNG",
        ),
    )
    return exg
