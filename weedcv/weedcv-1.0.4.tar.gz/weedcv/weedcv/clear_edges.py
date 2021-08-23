import os
from pathlib import Path

from skimage.segmentation import clear_border

from weedcv.weedcv import params
from weedcv.weedcv._debug import _debug


def clear_edges(bin_img):
    """
    Denoising by removing vegetations that extend beyond image frame.
    Input:
    binary_img = np array

    Output:
    cleared_binary = np array
    """
    cleared_binary = clear_border(bin_img)

    # Print or plot the binary image if debug is on
    _debug(
        cleared_binary,
        filename=Path(
            params.debug_outdir,
            str(params.debug_filename) + "_" + str(params.device) + ".PNG",
        ),
    )

    return cleared_binary
