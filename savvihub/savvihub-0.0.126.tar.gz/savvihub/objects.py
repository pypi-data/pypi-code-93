import os
from typing import Optional, Union

import six
from PIL import Image as PIL_Image

from savvihub.constants import SAVVIHUB_IMAGES
from savvihub.utils import get_type_name, generate_uuid, to_uint8


class Image:
    def __init__(
        self,
        data: Union[str, "Image", "PIL.Image", "np.ndarray"],
        caption: Optional[str] = None,
        mode: Optional[str] = None
    ):
        self._image = None
        self._caption = None
        self._mode = None
        self._path = None

        self._init_meta(caption, mode)
        self._init_image(data)
        self._save_image()

    def _init_meta(self, caption, mode):
        self._caption = caption
        self._mode = mode

        if not os.path.exists(SAVVIHUB_IMAGES):
            os.makedirs(SAVVIHUB_IMAGES)

        self._path = os.path.join(SAVVIHUB_IMAGES, generate_uuid() + '.png')

    def _init_image_from_path(self, data):
        if not os.path.isfile(data):
            print(f'Error: {data} file not found')
        self._image = PIL_Image.open(data)

    def _init_image_from_data(self, data):
        if get_type_name(data).startswith("torch."):
            self._image = PIL_Image.fromarray(
                data.mul(255).clamp(0, 255).byte().permute(1, 2, 0).squeeze().cpu().numpy()
            )
        elif isinstance(data, PIL_Image.Image):
            self._image = data
        else:
            if hasattr(data, "numpy"):
                data = data.numpy()
            if data.ndim > 2:
                data = data.squeeze()
            self._image = PIL_Image.fromarray(
                to_uint8(data), mode=self._mode,
            )

    def _init_image(self, data):
        if isinstance(data, Image):
            self._image = data._image
        elif isinstance(data, six.string_types):
            self._init_image_from_path(data)
        else:
            self._init_image_from_data(data)

    def _save_image(self):
        self._image.save(self._path)

    def flush(self):
        if os.path.isfile(self._path):
            os.remove(self._path)
        else:
            print(f'Error: {self._path} file not found')

    def get_path(self):
        return self._path

    def get_caption(self):
        return self._caption
