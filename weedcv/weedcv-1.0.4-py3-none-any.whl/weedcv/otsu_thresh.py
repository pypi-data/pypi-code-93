from pathlib import Path

import cv2

from weedcv.weedcv import params
from weedcv.weedcv._debug import _debug


def otsu_thresh(mask, method_name="_otsu_thresh_", kernel_size=(3, 3)):
    """
    Denoises mask and/or grayscale image by first applying
    a gaussian filter then using Otsu's thresholding.

    Inputs:
    mask        = gray scale image (uint8 single-channel np array)

    Outputs:
    mask_th = binary image (np array)
    """

    mask_blur = cv2.GaussianBlur(mask, kernel_size, 0).astype("uint8")
    adaptive_method = cv2.THRESH_BINARY + cv2.THRESH_OTSU

    ret, bin_img = cv2.threshold(mask_blur, 0, 255, adaptive_method)

    # Threshold the image
    _debug(
        bin_img,
        filename=Path(
            params.debug_outdir,
            str(params.debug_filename) + "_" + str(params.device) + "_otsu.PNG",
        ),
    )

    return bin_img
