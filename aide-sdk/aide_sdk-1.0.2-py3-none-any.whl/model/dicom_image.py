import os

import pydicom
from pydicom.uid import generate_uid

from aide_sdk.logger.logger import LogManager
from aide_sdk.utils.dicom import dataset_to_dict

logger = LogManager._get_audit_logger()


class DicomImage:
    def __init__(self, image_path: str, load_metadata=False):
        self.image_path = image_path
        self.context_metadata = self.reload_context_metadata() if load_metadata else dict()

    def load_dataset(self) -> pydicom.Dataset:
        """Loads a pydicom.Dataset object from storage for the image_path of the
        DicomImage.

        If no image can be found in storage a FileNotFoundError will be raised.
        :return: a pydicom.Dataset object representing the DICOM file in storage.
        """

        try:
            dataset = pydicom.dcmread(self.image_path)

            logger.info("Model has loaded DICOM image dataset from storage",
                        extra={"props": {"file": self.image_path}})

            return dataset
        except FileNotFoundError:
            logger.exception(
                "Model has failed to load DICOM image dataset from storage",
                extra={"props": {
                    "file": self.image_path
                }})
            raise

    def get_filename(self) -> str:
        """Returns the filename of the DicomImage in storage

        :return: the filename of the DicomImage in storage with the '.dcm'
        suffix.
        """
        if not self.image_path:
            return ""

        split = self.image_path.rsplit(os.sep, 1)
        filename = split[1]
        return filename

    def get_context_metadata(self):
        if not self.context_metadata:
            return self.reload_context_metadata()

        return self.context_metadata

    def reload_context_metadata(self):
        dataset = self.load_dataset()
        self.context_metadata = dataset_to_dict(dataset)
        return self.context_metadata

    def __eq__(self, other):
        if not isinstance(other, DicomImage):
            return False

        return self.image_path == other.image_path

    @classmethod
    def generate_unique_id(cls):
        return generate_uid()
