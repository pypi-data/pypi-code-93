import torch
from .petrel import PetrelDataset


class TrainDataset(PetrelDataset):
    """
    Dataset class for training data. Performs the preprocessing transformation up to max_iter times, stopping if
    there is at least one bounding box in the transformed image. Performs another preprocessing transformation
    if the first cannot produce bounding boxes.
    """

    def __init__(self, meta_data,
                 boxes,
                 image_root,
                 transform,
                 backup_transform=None,
                 max_iter=100):
        """
        :param meta_data: DataFrame consisting of metadata for dataset. Must be one row per datapoint.
        :param boxes: DataFrame consisting of all bounding box data for dataset. Must be in PASCAL VOC format, with
        xmin, ymin, xmax, ymax in separate columns. Must also include numeric label column.
        :param image_root: Root directory for imge files.
        :param transform: Any preprocessing transformations used in preparing the data. Usually Albumentations.
        :param backup_transform: Optional second transform to use if the first does not produce output with bounding boxes.
        :param max_iter: Maximum number of times to try transform.
        """
        super(TrainDataset, self).__init__(meta_data, boxes, image_root, transform, train_pipe=True)
        self.backup_transform = backup_transform if backup_transform else transform
        self.max_iter = max_iter

    def __getitem__(self, index):
        """
        Retrieves the image and boxes with the specified index.
        :param index: Index of the meta_data row for the item to be loaded.
        :return: Image and target dictionary consisting of bounding boxes and labels.
        """

        image_meta = self.meta_data.loc[index]
        image_boxes = self.boxes[self.boxes["file"] == image_meta["file"]]
        image, bboxes, labels = self.load_image_and_boxes(image_meta, image_boxes)
        target = {"bboxes": bboxes,
                  "labels": labels}
        # Try standard transform in bounding boxes present in raw image.
        if self.transform and bboxes.shape[0] > 0:
            # Try the standard transformation up to max_iter times.
            for _ in range(self.max_iter):
                sample = self.transform(image=image,
                                        bboxes=target["bboxes"],
                                        labels=target["labels"])
                ## Return preprocessed image if bounding boxes present.
                if len(sample["bboxes"]) > 0:
                    image, target["bboxes"] = sample["image"], self._box_to_tensor(sample["bboxes"])
                    target["labels"] = torch.tensor(sample["labels"])
                    return image, target
        # Apply the backup transform if the standard transform failed.
        sample = self.backup_transform(image=image,
                                       bboxes=target["bboxes"],
                                       labels=target["labels"])
        image, target["bboxes"] = sample["image"], self._box_to_tensor(sample["bboxes"])
        target["labels"] = torch.tensor(sample["labels"])
        return image, target
