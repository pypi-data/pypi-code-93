import json
import os

import pytest
import torch

from PIL import Image

from azureml.automl.dnn.vision.common.exceptions import AutoMLVisionDataException
from azureml.automl.dnn.vision.object_detection.data.datasets import FileObjectDetectionDatasetWrapper
from azureml.automl.dnn.vision.object_detection.common.augmentations import transform


@pytest.mark.usefixtures('new_clean_dir')
class TestCommonObjectDetectionDatasetWrapper:
    def _read_annotations_file(self, annotations_file):
        annotations = []

        with open(annotations_file, "r") as json_file:
            for line in json_file:
                annotations.append(json.loads(line))
        return annotations

    def test_missing_annotations(self):
        missing_annotations_file = 'object_detection_data/annotation_missing_image_dimensions.json'
        image_root = 'object_detection_data/images'
        dataset_wrapper = FileObjectDetectionDatasetWrapper(annotations_file=missing_annotations_file,
                                                            image_folder=image_root)

        assert len(dataset_wrapper) == 1
        image, boxes_labels_dict, details = dataset_wrapper[0]

        assert details['width'] > 100
        assert details['height'] > 100

        box = boxes_labels_dict['boxes'][0]
        assert all([box[0].item() > 1 and box[1].item() > 1 and box[2].item() > 1 and box[3].item() > 1])

    def test_all_images_in_annotations_are_ill_formed(self):
        missing_annotations_file = 'object_detection_data/annotation_all_images_ill_formed.json'
        image_root = 'object_detection_data/images'
        with pytest.raises(AutoMLVisionDataException):
            FileObjectDetectionDatasetWrapper(annotations_file=missing_annotations_file, image_folder=image_root)

    def test_transform_when_training(self):
        annotations_file = 'object_detection_data/annotation_missing_image_dimensions.json'
        image_root = 'object_detection_data/images'

        annotations = self._read_annotations_file(annotations_file)
        image_url = os.path.join(image_root, annotations[0]['imageUrl'])
        image = Image.open(image_url).convert('RGB')
        train_dataset_wrapper = FileObjectDetectionDatasetWrapper(annotations_file=annotations_file,
                                                                  image_folder=image_root,
                                                                  is_train=True)

        transformed_image, boxes_labels_dict, details = train_dataset_wrapper[0]
        assert details['width'] * details['height'] > image.width * image.height * 0.6
        bbox_area = (boxes_labels_dict['boxes'][0][2] - boxes_labels_dict['boxes'][0][0]) * \
                    (boxes_labels_dict['boxes'][0][3] - boxes_labels_dict['boxes'][0][1])
        assert int(details['areas'][0]) == int(bbox_area)

    def test_transform_with_bad_boxes(self):
        annotations_file = 'object_detection_data/annotation_bad_box_coordinates.json'
        image_root = 'object_detection_data/images'

        annotations = self._read_annotations_file(annotations_file)
        image_url = os.path.join(image_root, annotations[0]['imageUrl'])
        image = Image.open(image_url).convert('RGB')

        width, height = image.width, image.height
        bounding_box = [annotations[0]['label']['topX'] * width,
                        annotations[0]['label']['topY'] * height,
                        annotations[0]['label']['bottomX'] * width,
                        annotations[0]['label']['bottomY'] * height]
        boxes = torch.as_tensor(bounding_box, dtype=torch.float32).unsqueeze(0)
        # data augmentations
        transformed_image, transformed_boxes, areas, height, width, _ = transform(
            image=image,
            boxes=boxes,
            is_train=True,
            prob=1.0,
            post_transform=None)

        assert any(coord < 0 for coord in transformed_boxes[0])
        bbox_area = (transformed_boxes[0][2] - transformed_boxes[0][0]) * \
                    (transformed_boxes[0][3] - transformed_boxes[0][1])
        assert int(areas[0]) == int(bbox_area.data)
