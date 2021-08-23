from pathlib import Path

import cv2

from weedcv.weedcv import params
from weedcv.weedcv._debug import _debug

"""
Adapted from Plantcv:
https://github.com/danforthcenter/plantcv/blob/master/plantcv/plantcv/readimage.py
"""


def load_img(path, mode="rgb"):
    """
    Read image from absolute image path.
    Inputs:
    path    = absolute image file path
    mode    = image format for output ("rgb", "bgr", "rgba", "gray")

    Returns:
    img     = image as numpy array
    path    = input path
    """
    if not Path(path).is_file():
        raise RuntimeError("Image path does not exists.")

    if mode.upper() == "RGB":
        img = cv2.imread(path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    elif mode.upper() == "BGR":
        img = cv2.imread(path)
    elif mode.upper() == "RGBA":
        img = cv2.imread(path, -1)
    elif mode.upper() == "GRAY" or mode.upper() == "GREY":
        img = cv2.imread(path, 0)
    if img is None:
        raise RuntimeError("Failed to open " + path)

    _debug(
        img,
        filename=Path(
            params.debug_outdir,
            str(params.debug_filename) + "_" + str(params.device) + "_input_image.PNG",
        ),
    )

    return img, path
