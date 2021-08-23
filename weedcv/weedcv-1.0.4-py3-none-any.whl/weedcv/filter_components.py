from pathlib import Path

import cv2
import numpy as np

from weedcv.weedcv import params
from weedcv.weedcv._debug import _debug


def filter_components(mask, top_n):
    # calculate size of individual components and chooses based on min size
    nb_components, output, stats, centroids = cv2.connectedComponentsWithStats(
        mask, connectivity=8
    )
    # size of components except 0 (background)
    sizes = stats[1:, -1]
    nb_components = nb_components - 1
    # Determines number of components to segment
    # Sort components from largest to smallest
    top_n_sizes = sorted(sizes, reverse=True)[:top_n]
    try:
        min_size = min(top_n_sizes) - 1
    except:
        min_size = 0
    list_filtered_masks = []
    for i in range(0, nb_components):
        if sizes[i] >= min_size:
            filtered_mask = np.zeros((output.shape))
            filtered_mask[output == i + 1] = 255
            list_filtered_masks.append(filtered_mask)

    for mask in list_filtered_masks:
        # Print or plot the binary image if debug is on
        _debug(
            mask,
            filename=Path(
                params.debug_outdir,
                str(params.debug_filename) + "_" + str(params.device) + ".PNG",
            ),
        )
    return list_filtered_masks
