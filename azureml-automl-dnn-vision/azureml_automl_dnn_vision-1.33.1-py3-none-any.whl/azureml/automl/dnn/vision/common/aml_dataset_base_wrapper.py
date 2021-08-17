# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Base Aml Dataset wrapper class to be used by classification and object detection"""
from typing import Any

from azureml.core import Dataset as AmlDataset
from azureml.core import Workspace

from .labeled_dataset_helper import AmlLabeledDatasetHelper


class AmlDatasetBaseWrapper:
    """Base class for aml dataset wrappers used in classification and object detection."""

    DATASET_IMAGE_COLUMN_NAME = AmlLabeledDatasetHelper.DEFAULT_IMAGE_COLUMN_NAME

    @classmethod
    def download_image_files(cls, dataset_id: str, workspace: Workspace,
                             datasetclass: Any = AmlDataset) -> None:
        """Download image files to a predefined local path.
        These files will be later used when the class is initiated.

        Please make sure that you set download_files to False in class init so that files are not downloaded again.

        :param dataset_id: dataset id
        :type dataset_id: str
        :param workspace: workspace object
        :type workspace: azureml.core.Workspace
        :param datasetclass: The source dataset class.
        :type datasetclass: class
        """
        ds = datasetclass.get_by_id(workspace, dataset_id)
        image_column_name = AmlLabeledDatasetHelper.get_image_column_name(ds, cls.DATASET_IMAGE_COLUMN_NAME)
        AmlLabeledDatasetHelper.download_image_files(ds, image_column_name)
