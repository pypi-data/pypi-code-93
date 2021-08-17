# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Dataset for prediction."""

import json
import os

from torch.utils.data import Dataset
from torchvision.transforms import Compose
from torch.tensor import Tensor
from azureml.automl.dnn.vision.common.logging_utils import get_logger
from azureml.automl.dnn.vision.common.utils import _read_image, _validate_image_exists
from azureml.automl.dnn.vision.common.labeled_dataset_helper import AmlLabeledDatasetHelper
from azureml.automl.dnn.vision.object_detection.common.constants import DatasetFieldLabels
from azureml.core import Dataset as AmlDataset
from azureml.core import Workspace
from azureml.automl.dnn.vision.common.exceptions import AutoMLVisionDataException
from typing import TypeVar, List, Any, Optional, Iterable, Tuple, cast

T_co = TypeVar('T_co', covariant=True)

logger = get_logger(__name__)


class PredictionDataset(Dataset[T_co]):
    """Dataset file so that score.py can process images in batches.

    """

    def __init__(self, root_dir: Optional[str] = None,
                 image_list_file: Optional[str] = None,
                 transforms: Optional[Compose] = None,
                 ignore_data_errors: bool = True,
                 input_dataset_id: Optional[str] = None,
                 ws: Optional[Workspace] = None,
                 datasetclass: Any = AmlDataset):
        """
        :param root_dir: prefix to be added to the paths contained in image_list_file
        :type root_dir: str
        :param image_list_file: path to file containing list of images
        :type image_list_file: str
        :param transforms: function that takes in a pillow image and can generate tensor
        :type transforms: function
        :param ignore_data_errors: boolean flag on whether to ignore input data errors
        :type ignore_data_errors: bool
        :param input_dataset_id: The input dataset id.  If this is specified image_list_file is not required.
        :type input_dataset_id: str
        :param ws: The Azure ML Workspace
        :type ws: Workspace
        :param datasetclass: The Azure ML Dataset class
        :type datasetclass: Dataset

        """
        self._files = []

        if input_dataset_id is not None:
            dataset_helper = AmlLabeledDatasetHelper(input_dataset_id, ws, ignore_data_errors,
                                                     image_column_name=AmlLabeledDatasetHelper.PATH_COLUMN_NAME,
                                                     datasetclass=datasetclass)
            self._files = dataset_helper.get_file_name_list()
            self._files = [f.strip("/") for f in self._files]
            self._root_dir = dataset_helper._data_dir
        else:
            self._files = self._get_files_from_image_list_file(root_dir, image_list_file, ignore_data_errors)
            self._root_dir = cast(str, root_dir)

        # Length of final dataset
        logger.info('Size of dataset: {}'.format(len(self._files)))
        self._transform = transforms
        self._ignore_data_errors = ignore_data_errors

    def __len__(self) -> int:
        """Size of the dataset."""
        return len(self._files)

    @staticmethod
    def collate_function(batch: Iterable[Any]) -> Tuple[Any, ...]:
        """Collate function for the dataset"""
        return tuple(zip(*batch))

    def __getitem__(self, idx: int) -> Tuple[str, Tensor]:
        """
        :param idx: index
        :type idx: int
        :return: item and label at index idx
        :rtype: tuple[str, image]
        """
        filename, full_path = self.get_image_full_path(idx)

        image = _read_image(self._ignore_data_errors, full_path)
        if image is not None:
            if self._transform:
                image = self._transform(image)

        return filename, image

    def get_image_full_path(self, idx: int) -> Tuple[str, str]:
        """Returns the filename and full file path for the given index.

        :param idx: index of the file to return
        :type idx: int
        :return: a tuple filename, full file path
        :rtype: tuple
        """
        filename = self._files[idx]
        if self._root_dir and filename:
            filename = filename.lstrip('/')
        full_path = os.path.join(self._root_dir, filename)
        return filename, full_path

    def _get_files_from_image_list_file(self, root_dir: Optional[str], image_list_file: Any,
                                        ignore_data_errors: bool = True) -> List[str]:
        files = []
        with open(image_list_file) as fp:
            lines = fp.readlines()
            parse_as_json_file = True
            if len(lines) > 0:
                try:
                    json.loads(lines[0])
                    logger.info("Parsing image list file as a JSON file")
                except json.JSONDecodeError:
                    parse_as_json_file = False

            if parse_as_json_file:
                files = self._parse_image_file_as_json(root_dir, lines, ignore_data_errors)
            else:
                for row in lines:
                    # filter out label info if present
                    file_data = row.split('\t')
                    filename = file_data[0].strip()
                    if not filename:
                        if not ignore_data_errors:
                            raise AutoMLVisionDataException('Input image file contains empty row', has_pii=False)
                        continue
                    full_path = os.path.join(root_dir, filename) if root_dir is not None else filename
                    if _validate_image_exists(full_path, ignore_data_errors):
                        files.append(filename)

        return files

    def _parse_image_file_as_json(self, root_dir: Optional[str], lines: List[str],
                                  ignore_data_errors: bool) -> List[str]:
        files = []
        for row in lines:
            try:
                annotation = json.loads(row)
                if DatasetFieldLabels.IMAGE_URL not in annotation:
                    missing_required_fields_message = "Missing required fields in annotation"
                    if not ignore_data_errors:
                        raise AutoMLVisionDataException(missing_required_fields_message, has_pii=False)
                    continue
                filename = annotation[DatasetFieldLabels.IMAGE_URL]
                filename = filename.strip()
                full_path = os.path.join(root_dir, filename) if root_dir is not None else filename
                if _validate_image_exists(full_path, ignore_data_errors):
                    files.append(filename)
            except json.JSONDecodeError:
                if not ignore_data_errors:
                    raise AutoMLVisionDataException("Invalid JSON object detected in file", has_pii=False)
                continue
        return files
