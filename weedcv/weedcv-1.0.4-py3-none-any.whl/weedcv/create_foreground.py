from pathlib import Path

import cv2
import numpy as np

from weedcv.weedcv import params
from weedcv.weedcv._debug import _debug


def create_foreground(img, mask):
    # applys mask to create RGBA foreground using np
    mask = np.dstack([mask] * 3)  # Create 3-channel alpha mask
    mask = mask.astype("float32") / 255.0  # Use float matrices,
    img = img.astype("float32") / 255.0  # for easy blending

    masked = (mask * img) + ((1 - mask) * 255)  # Blend
    masked = (masked * 255).astype("uint8")

    _debug(
        masked,
        filename=Path(
            params.debug_outdir,
            params.debug_filename + "_" + str(params.device) + "_foreground.PNG",
        ),
    )
    return masked
