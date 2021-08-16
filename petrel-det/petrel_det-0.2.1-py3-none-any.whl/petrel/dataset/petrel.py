from abc import ABC

import numpy as np
import cv2
import torch
from torch.utils.data import Dataset


class PetrelDataset(Dataset, ABC):
    """Dataset class for data used in Petrel models."""
    def __init__(self, meta_data,
                 boxes,
                 image_root,
                 transform=None,
                 train_pipe=False):
        """
        :param meta_data: DataFrame consisting of metadata for dataset. Must be one row per datapoint.
        :param boxes: DataFrame consisting of all bounding box data for dataset. Must be in PASCAL VOC format, with
        xmin, ymin, xmax, ymax in separate columns. Must also include numeric label column.
        :param image_root: Root directory for imge files.
        :param transform: Any preprocessing transformations used in preparing the data. Usually Albumentations.
        :param train_pipe: Is ths dataset used for training prediction. Training requires yxyx while prediction
        requires xyxy. Defaults to False.
        """
        super(PetrelDataset).__init__()

        self.meta_data = meta_data
        self.boxes = boxes
        self.image_root = image_root
        self.transform = transform
        self.train_pipe = train_pipe

    def _box_to_tensor(self, boxes):
        """
        Converts bounding box data to PyTorch tensor.
        :param boxes: List of bounding boxes.
        :return: Bounding box tensor.
        """
        bboxes = torch.tensor(boxes) if len(boxes) > 0 else torch.zeros((0, 4))
        # Convert bounded box to yxyx format if in training pipline
        if self.train_pipe:
            bboxes[:, [0, 1, 2, 3]] = bboxes[:, [1, 0, 3, 2]]
        return bboxes

    def __len__(self) :
        """
        Returns the size of the dataset.
        :return: Size of the dataset.
        """
        return self.meta_data.shape[0]

    def load_image_and_boxes(self, image_meta, image_boxes):
        """
        Loads single image with all bounding boxes and associated labels
        :param image_meta: DataFrame row consisting of data for the single image.
        :param image_boxes: DataFrame of bounding boxes and labels for the image.
        :return: Image, bounding boxes, and labels.
        """
        image = cv2.cvtColor(
            cv2.imread(f"{self.image_root}/{image_meta['file']}",
                       cv2.IMREAD_COLOR),
            cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
        bboxes = image_boxes[["xmin", "ymin", "xmax", "ymax"]].values
        bboxes = torch.tensor(bboxes)
        if "labels" in image_boxes.columns:
            labels = torch.tensor(image_boxes["labels"].values,
                                  dtype=torch.int64)
        else:
            labels = torch.tensor(np.ones(bboxes.shape[0]),
                                  dtype=torch.int64)
        return image, bboxes, labels
