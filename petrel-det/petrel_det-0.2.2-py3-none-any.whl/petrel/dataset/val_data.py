import torch
from .petrel import PetrelDataset


class ValDataset(PetrelDataset):
    """
    Dataset class for validation data. Performs one preprocessing transformation on the raw data.
    """

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
        :param train_pipe: Is the dataset being used in a training pipeline. Needed to determine
        """
        super(ValDataset, self).__init__(meta_data, boxes, image_root, transform, train_pipe)

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

        if self.transform:
            sample = self.transform(image=image,
                                    bboxes=target["bboxes"],
                                    labels=target["labels"])
            image, target["bboxes"] = sample['image'], self._box_to_tensor(sample["bboxes"])
            target["labels"] = torch.tensor(sample["labels"])
        return image, target
