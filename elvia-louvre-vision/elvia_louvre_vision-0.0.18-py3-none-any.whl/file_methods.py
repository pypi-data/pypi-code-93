import json
from typing import List, Optional, Tuple, Union

from louvre_vision.data_models import ClassificationTrainingImage, ImageRegion, ObjectDetectionTrainingImage, RegionBoundingBox
from louvre_vision.dataset import ClassificationDataset, ObjectDetectionDataset
from .methods import Methods


class FileMethods:
    """
    Methods related to file manipulation.    
    """
    @staticmethod
    def get_classification_dataset_from_csv(
            dataset_path: str,
            identifier_column: int,
            label_column: int,
            remove_titles: bool = False,
            delimiter: Optional[str] = None,
            serialised_labels: bool = True) -> ClassificationDataset:
        """Import a classification dataset from a CSV file."""

        dataset_list = Methods.get_dataset_from_csv(
            dataset_path=dataset_path,
            remove_titles=remove_titles,
            delimiter=delimiter)[1]

        for index in range(0, len(dataset_list)):
            if serialised_labels:
                labels = json.loads(dataset_list[index][label_column])
            else:
                labels = [dataset_list[index][label_column]]
            dataset_list[index] = ClassificationTrainingImage(
                identifier=dataset_list[index][identifier_column],
                labels=labels)

        return ClassificationDataset(images=dataset_list)

    @staticmethod
    def get_object_detection_dataset_from_csv(
            dataset_path: str,
            identifier_column: int,
            regions_column: int,
            remove_titles: bool = False,
            delimiter: Optional[str] = None) -> ObjectDetectionDataset:
        """Import an object detection dataset from a CSV file."""

        dataset_list = Methods.get_dataset_from_csv(
            dataset_path=dataset_path,
            remove_titles=remove_titles,
            delimiter=delimiter)[1]

        result: List[ObjectDetectionTrainingImage] = []
        for index in range(0, len(dataset_list)):
            identifier, regions = FileMethods._extract_object_detection_training_image(
                input_list=dataset_list[index],
                identifier_column=identifier_column,
                regions_column=regions_column)
            if identifier:
                result.append(
                    ObjectDetectionTrainingImage(identifier=identifier,
                                                 regions=regions))
        return ObjectDetectionDataset(images=result)

    @staticmethod
    def save_classification_dataset_to_csv(file_path: str,
                                           dataset: ClassificationDataset,
                                           delimiter: Optional[str] = None,
                                           append: bool = False) -> None:
        """Save classification images to a CSV file."""

        dataset_list = []
        for image in dataset.images:
            dataset_list.append([image.identifier, json.dumps(image.labels)])

        Methods.save_dataset_to_csv(file_path=file_path,
                                    dataset=dataset_list,
                                    delimiter=delimiter,
                                    append=append)

    @staticmethod
    def save_object_detection_dataset_to_csv(file_path: str,
                                             dataset: ObjectDetectionDataset,
                                             delimiter: Optional[str] = None,
                                             append: bool = False) -> None:
        """Save object detection images to a CSV file."""

        dataset_list = []
        for image in dataset.images:
            dataset_list.append([
                image.identifier,
                json.dumps([region.to_dict() for region in image.regions])
            ])

        Methods.save_dataset_to_csv(file_path=file_path,
                                    dataset=dataset_list,
                                    delimiter=delimiter,
                                    append=append)

    @staticmethod
    def _extract_object_detection_training_image(
            input_list: List[str], identifier_column: int,
            regions_column: int) -> Tuple[Union[str, None], List[ImageRegion]]:

        identifier = input_list[identifier_column] if len(
            input_list
        ) > identifier_column and input_list[identifier_column] and isinstance(
            input_list[identifier_column], str) else None
        regions = FileMethods._extract_image_regions(
            json.loads(input_list[regions_column])
        ) if len(input_list
                 ) > regions_column and input_list[regions_column] else []
        return identifier, regions

    @staticmethod
    def _extract_image_regions(
            serialised_regions: List[str]) -> List[ImageRegion]:
        regions: List[ImageRegion] = []
        region_keys = ['top', 'left', 'width', 'height', 'tag_name']

        if not isinstance(serialised_regions, list):
            return regions

        for region in serialised_regions:
            if not isinstance(region, dict) or not all(
                    True for key in region_keys if key in region.keys()):
                continue
            top = Methods.cast_to_float(region.get('top', None))
            left = Methods.cast_to_float(region.get('left', None))
            width = Methods.cast_to_float(region.get('width', None))
            height = Methods.cast_to_float(region.get('height', None))
            tag_name = region.get('tag_name', None)
            if top and left and width and height and tag_name:
                bounding_box = RegionBoundingBox(top=top,
                                                 left=left,
                                                 width=width,
                                                 height=height)
                regions.append(
                    ImageRegion(tag_name=tag_name, bounding_box=bounding_box))
        return regions
