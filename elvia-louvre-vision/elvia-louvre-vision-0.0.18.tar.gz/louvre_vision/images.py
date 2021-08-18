from dataclasses import dataclass
from elvia_louvre.image_api import ImageData
import imageio
from imgaug import augmenters as iaa
import io
import numpy as np
from numpy import asarray
from PIL import Image
from typing import Dict, Optional, Union

from louvre_vision.config import Config
from louvre_vision.errors import LouvreVisionValueError
from louvre_vision.methods import Methods


@dataclass
class ImageEntry:
    """
    Represents an image file in Louvre.
    """
    sasuri: Optional[str] = None
    file_bytes: Optional[bytes] = None

    @property
    def is_empty(self) -> bool:
        return self.sasuri is None and self.file_bytes is None


class ImageMethods:
    """
    Class with helper methods to handle images.
    """
    @staticmethod
    def resize_from_url(image_url: str, image_longer_side: int) -> bytes:
        """
        Fetch an image from a URL and resize it.
        
        :param str image_url: Image URL
        :param int image_longer_side: Desired pixel length for the longer side of the image. Aspect ratio is kept constant.
        :returns: The resized image as bytes 
        :rtype: bytes
        :raises RequestException:
        :raises LouvreVisionValueError:
        """
        image_fetched = Methods.fetch_file_from_url(image_url)
        if Methods.is_file_empty(image_fetched):
            raise LouvreVisionValueError(f'Image file is empty: {image_url}')

        image_size: Dict[str, Union[str, int]] = {
            'longer-side': image_longer_side,
            'shorter-side': 'keep-aspect-ratio'
        }
        base_image = ImageMethods.resize(Image.open(image_fetched), image_size)
        return ImageMethods._to_bytes(base_image)

    @staticmethod
    def get_image_from_image_data(image_data: ImageData,
                                  max_file_size: int) -> ImageEntry:
        """
        Return either an image sasuri or a resized image as bytes.

        :param ImageData image_data: ImageData coming from ImageAPI containing image data for a given ImageId.
        :param int max_file_size : Maximum image file size allowed, in bytes.
        :rtype: ImageEntry
        :raises LouvreVisionValueError:
        :raises RequestException:
        """
        # First ensure that there are images
        if len(image_data.image_files) == 0:
            return ImageEntry()

        # If the default variant is an up-sampling of "original", prefer the original
        chosen_variant: str = ImageMethods.select_preferred_image_variant_for_custom_vision(
            image_data=image_data)

        image_variant = image_data.get_variant(chosen_variant)
        if image_variant:
            if image_variant.size < max_file_size:
                return ImageEntry(sasuri=image_variant.sasuri)
            # If the image is too large, resize it
            return ImageEntry(file_bytes=ImageMethods.resize_from_url(
                image_url=image_variant.sasuri,
                image_longer_side=Config.image_longer_side))

        return ImageEntry()

    @staticmethod
    def select_preferred_image_variant_for_custom_vision(
            image_data: ImageData) -> str:
        """
        Return the preferred image variant.

        :param ImageData image_data:
        :rtype: str
        """
        _chosen_variant: str = Config.default_image_variant
        if 'original' in image_data.image_variants and Config.default_image_variant in image_data.image_variants:
            original = image_data.get_variant('original')
            default = image_data.get_variant(Config.default_image_variant)
            if original and default and original.height < default.height:
                _chosen_variant = 'original'
        return _chosen_variant

    @staticmethod
    def resize(input_image: Union[str, object],
               size: Union[Dict[str, Union[str, int]], str, int]) -> Image:
        """
        Resize image.

        :param input_image: Image to resize as either a file path or an Image object. 
        :type input_image: str | Image 
        :pararm size: Desired image resize choice, formatted as expected by the imgaug library https://imgaug.readthedocs.io/en/latest/source/api_augmenters_size.html#imgaug.augmenters.size.Resize
        :type size: Dict[str, Union[str, int]] | str | int
        :rtype: PIL.Image            
        """
        resize = iaa.Resize(size=size)
        input_img_array = ImageMethods._image_as_array(input_image)
        result_array = resize(image=input_img_array)
        result = Image.fromarray(result_array)
        return result

    @staticmethod
    def _image_as_array(input_image: Union[str, object]) -> np.ndarray:

        if isinstance(input_image, str):
            input_img_array = imageio.imread(
                input_image
            )  # imread should be able to read both local files and web resources
        else:
            input_img_array = asarray(input_image)
        return input_img_array

    @staticmethod
    def _to_bytes(img: Image.Image, img_format: str = 'JPEG') -> bytes:
        """
        Return image in the format required by the training client.
        """
        bytesio_stream = io.BytesIO()
        img.save(bytesio_stream, format=img_format)
        bytesio_stream.seek(0)
        the_data = bytesio_stream.getvalue()

        return the_data
