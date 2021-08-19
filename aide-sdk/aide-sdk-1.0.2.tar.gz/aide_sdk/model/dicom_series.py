import dataclasses
import os
from typing import Optional, List, Dict

from pydicom.uid import generate_uid

from aide_sdk.model.dicom_image import DicomImage


@dataclasses.dataclass(eq=True)
class DicomSeries:
    series_id: str
    folder_path: str
    metadata: Dict
    _images: Optional[List] = dataclasses.field(default=None, init=False)

    @property
    def images(self):
        """
        Load the images in this series from disk
        """
        if not self._images:
            self._images = []
            for item in os.scandir(self.folder_path):
                self._images.append(DicomImage(image_path=item.path))
        return self._images

    @classmethod
    def generate_unique_id(cls):
        return generate_uid()
