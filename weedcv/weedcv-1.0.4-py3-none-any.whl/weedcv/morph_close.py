from pathlib import Path

import skimage.morphology as morphology
from skimage.morphology import black_tophat, disk, opening, white_tophat

from weedcv.weedcv import otsu_thresh, params
from weedcv.weedcv._debug import _debug


def morph_close(mask, min_object_size, area_threshold):
    mask = morphology.remove_small_holes(
        morphology.remove_small_objects(mask.astype("uint8"), min_object_size),
        area_threshold,
    )

    # Close using white tophat
    w_disk = disk(4)
    # Close using black tophat
    b_disk = disk(2)
    # Tophat closing
    w_tophat = white_tophat(mask, w_disk)
    b_tophat = black_tophat(mask, b_disk)
    # Map results to mask
    mask[w_tophat == 255] = 255
    mask[b_tophat == 255] = 255
    # Otsu's thresh
    otsu_mask = otsu_thresh(mask.astype("uint8"))
    open_disk = disk(1)
    mask = opening(otsu_mask, open_disk)

    _debug(
        mask,
        filename=Path(
            params.debug_outdir,
            str(params.debug_filename) + "_" + str(params.device) + "_morph_close.PNG",
        ),
    )

    return mask
