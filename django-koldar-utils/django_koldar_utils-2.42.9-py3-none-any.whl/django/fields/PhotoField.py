import io
import math
import os
import uuid
from typing import Tuple, List, Dict, Optional, Union

from PIL.Image import Image
from datasize import DataSize
from django.core.exceptions import ValidationError
from django.core.files import File
from django.db import models, transaction

from django_koldar_utils.django.AbstractDjangoField import AbstractDjangoField
from django_koldar_utils.django.validators import validators
from django_koldar_utils.functions import image_helpers, math_helpers, secrets_helper


class PhotoField(models.ImageField):
    """
    A picture that is automatically resized to a maximum value
    if the user sends a bigger picture. The behavior is independent on validators
    """

    description = "Represents a photo the user uploads"

    def __init__(self, *args, image_format: str = None, delete_previous_image:bool = True, delete_default_if_commanded: bool = False, min_width: int = 32, min_height: int = 32, max_width: int = 256, max_height: int = 256, **kwargs):
        self.min_width = min_width
        """
        minimum width a picture can have
        """
        self.min_height = min_height
        """
        maximum width a picture can have
        """
        self.max_width = max_width
        """
        minimum height a picture can have
        """
        self.max_height = max_height
        """
        maximum height a picture can have
        """
        self.delete_previous_image = delete_previous_image
        """
        If true, we will delete the image from the physical system
        """
        self.delete_default_if_commanded = delete_default_if_commanded
        """
        If delete_previous_image is set and the iamge is the defualt one,
        we will delete the default image. If this is not what you wnat, set ti to false
        """
        self.image_format: Optional[str] = image_format
        """
        The format of the images that we will store in the database.
        If None we will not perform any conversion betweent he uploaded pictures and the persisted ones
        """

        super().__init__(*args, **kwargs)

    def deconstruct(self) -> Tuple[str, str, List[any], Dict[str, any]]:
        name, path, args, kwargs = super().deconstruct()
        kwargs["min_width"] = self.min_width
        kwargs["min_height"] = self.min_height
        kwargs["max_width"] = self.max_width
        kwargs["max_height"] = self.max_height
        kwargs["delete_previous_image"] = self.delete_previous_image
        kwargs["delete_default_if_commanded"] = self.delete_default_if_commanded

        return name, path, args, kwargs

    def save(self, image: Union[Image, str, bytes, bytearray], call_validators: bool = True) -> Image:
        """
        An upgraded version of ImageField.save().
        Save the image to the "uploaded_to" storage.

        The method can accpet a pillow Image, a path or even a byte array.
        It will autoamtically delete the previous iamge and scale the image correctly.
        This method will persist the image to the storage as well.

        :param image: either a pillow image, a filepath, bytes or bytearrow representing
        an image
        :param call_validators: if True, we will check if the image is correct before doing anything else
        """
        if isinstance(image, str):
            with open(image, mode="rb") as f:
                array = f.read()
                blob = io.BytesIO(array)
            new_profile_image = f"{os.path.dirname(image)}{os.path.basename(image)}_{secrets_helper.get_random_alphanum_str(10)}"
        elif isinstance(image, Image):
            blob = io.BytesIO()
            image.save(blob, 'png')
            new_profile_image = f"image_{secrets_helper.get_random_alphanum_str(10)}"
        elif isinstance(image, bytes):
            blob = io.BytesIO(image)
            new_profile_image = f"image_{secrets_helper.get_random_alphanum_str(10)}"
        elif isinstance(image, bytearray):
            blob = io.BytesIO(image)
            new_profile_image = f"image_{secrets_helper.get_random_alphanum_str(10)}"
        else:
            raise TypeError(f"invalid image {type(image)}!")

        # save image last value
        previous_image = getattr(self, self.attname).name
        # Check validators

        # this will delete the previous image in the storage
        if self.delete_previous_image:
            if previous_image != self.default or (previous_image == self.default and self.delete_default_if_commanded):
                self.delete(save=False)

        with transaction.atomic():
            if call_validators:
                self.full_clean()
            result = super().save(new_profile_image, File(blob))

        return result

    def pre_save(self, model_instance, add: bool) -> Image:
        image = image_helpers.get_image(filepath=model_instance.photo)

        w = math_helpers.bound(image.width, self.min_width, self.max_width)
        h = math_helpers.bound(image.height, self.min_height, self.max_height)

        if w != image.width or h != image.height:
            image = image_helpers.scale_image(image, w, h)

        setattr(model_instance, self.attname, image)
        return image

    def to_python(self, image) -> Optional[Image]:
        if image is None:
            return None

        if isinstance(image, bytes):
            im = Image.open(io.BytesIO(image))
        elif isinstance(image, str):
            im = Image.open(image.encode("utf8"))
        elif isinstance(image, Image):
            im = image
        else:
            raise TypeError(f"Cannot handle type {type(image)}!")

        return im

        # try:
        #     limit = DataSize(self.picture_threshold)
        #     num_of_tries = 10
        #     img = Image.open(image.file)
        #     width, height = img.size
        #     ratio = float(width) / float(height)
        #
        #     if settings.FILE_UPLOAD_TEMP_DIR is not None:
        #         upload_dir = settings.FILE_UPLOAD_TEMP_DIR
        #     else:
        #         upload_dir = "/tmp"
        #
        #     tmp_file = open(os.path.join(upload_dir, str(uuid.uuid1())), "w")
        #     tmp_file.write(image.file.read())
        #     tmp_file.close()
        #
        #     while os.path.getsize(tmp_file.name) > limit:
        #         num_of_tries -= 1
        #         width = 900 if num_of_tries == 0 else width - 100
        #         height = int(width / ratio)
        #         img.thumbnail((width, height), Image.ANTIALIAS)
        #         img.save(tmp_file.name, img.format)
        #         image.file = open(tmp_file.name)
        #         if num_of_tries == 0:
        #             break
        # except:
        #     pass
        # return image


