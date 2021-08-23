# from weedcv.weedcv import apply_mask
from pathlib import Path

import numpy as np

from weedcv.weedcv import params
from weedcv.weedcv._debug import _debug


def combine_component(component_list):
    input_img_shape = component_list[0].shape
    comb_mask = np.zeros(input_img_shape)
    for component in component_list:
        comb_mask[np.where(component != 0)] = 255

    _debug(
        comb_mask,
        filename=Path(
            params.debug_outdir,
            params.debug_filename + "_" + str(params.device) + "_combined_mask.PNG",
        ),
    )
    return comb_mask
