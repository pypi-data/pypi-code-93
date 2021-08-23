# Debugging module
from pathlib import Path
from re import search

import cv2

from weedcv.weedcv import params, save_image
from weedcv.weedcv.show_image import show_images


def _debug(visual, filename=None):
    """
    Adapted from plantcv
    https://github.com/danforthcenter/plantcv/blob/master/plantcv/plantcv/_debug.py

    Save or display a visual for debugging.
    Inputs:
    visual   - An image or plot to display for debugging
    save_path - An optional filename to save the visual to (default: None)
    :param visual: numpy.ndarray
    :param filename: str
    """
    # Auto-increment the device counter
    params.device += 1

    if params.debug.lower() == "show":
        # show the image using opencv imshow
        show_images(visual=visual, filename=filename)

    elif params.debug.lower() == "save":
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        # save results to "save" directory
        save_image(visual=visual, filename=filename)

    elif params.debug.lower() == "input_image":
        if search(params.debug, filename.parts[-1]):
            Path(filename).parent.mkdir(parents=True, exist_ok=True)
            save_image(visual=visual, filename=filename)

        else:
            pass

    elif params.debug.lower() == "exg":
        if search(params.debug, filename.parts[-1]):
            Path(filename).parent.mkdir(parents=True, exist_ok=True)
            save_image(visual=visual, filename=filename)
        else:
            pass

    elif params.debug.lower() == "otsu":
        if search(params.debug, filename.parts[-1]):
            Path(filename).parent.mkdir(parents=True, exist_ok=True)
            save_image(visual=visual, filename=filename)
        else:
            pass
    elif params.debug.lower() == "mask":
        if search(params.debug, filename.parts[-1]):
            Path(filename).parent.mkdir(parents=True, exist_ok=True)
            save_image(visual=visual, filename=filename)
        else:
            pass

    elif params.debug.lower() == "combined_mask":
        if search(params.debug, filename.parts[-1]):
            Path(filename).parent.mkdir(parents=True, exist_ok=True)
            save_image(visual=visual, filename=filename)
        else:
            pass

    elif params.debug.lower() == "foreground":
        if search(params.debug, filename.parts[-1]):
            Path(filename).parent.mkdir(parents=True, exist_ok=True)
            save_image(visual=visual, filename=filename)
        else:
            pass

    elif params.debug is None:
        pass


#     elif params.debug == "debug exg":
# window = params.debug
# visual = cv2.resize(visual, (600, 400))
# cv2.imshow(window, visual)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
#         # If debug is print, save the image to a file
# print_image(visual=visual, save_path=save_path)
