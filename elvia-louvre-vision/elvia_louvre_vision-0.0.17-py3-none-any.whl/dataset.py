from abc import abstractmethod
from dataclasses import dataclass
import hashlib
from typing import Counter, List, Optional, Set, Union

from .config import Config
from .data_models import ClassificationTrainingImage, ObjectDetectionTrainingImage, TrainingImage


@dataclass
class TagFrequency:
    """Describe how much of a tag there is in a dataset."""

    tag_name: str
    images: int
    bounding_boxes: Optional[int] = None


class Dataset(List[TrainingImage]):
    """Base class to represent datasets."""

    images: Union[List[ClassificationTrainingImage],
                  List[ObjectDetectionTrainingImage]]

    @property
    def duplicates(self) -> set:
        return set([
            image for image in self.images if Counter(self.images)[image] > 1
        ])

    @property
    def hash(self) -> Optional[str]:
        """Return a hash value based on the dataset contents."""
        # It doesn't matter how we sort as long as we always do it in the same way
        if len(self.images) == 0:
            return None
        self.images.sort()
        _hash = hashlib.sha256()
        _hash.update(str(self.images).encode())
        return _hash.hexdigest()[:Config.hash_length]

    @property
    @abstractmethod
    def unique_images(
            self) -> Union['ClassificationDataset', 'ObjectDetectionDataset']:
        raise NotImplementedError()

    @property
    @abstractmethod
    def unique_tags(self) -> Set[str]:
        return NotImplemented

    @property
    @abstractmethod
    def attributes(self) -> List[TagFrequency]:
        return NotImplemented


class ClassificationDataset(Dataset):

    images: List[ClassificationTrainingImage]

    def __init__(self, images: List[ClassificationTrainingImage]):
        self.images = images

    @property
    def unique_images(self) -> 'ClassificationDataset':
        return ClassificationDataset(sorted(list(set(self.images))))

    @property
    def unique_tags(self) -> Set[str]:
        #[x for b in a for x in b]
        """Return the unique tag names present in the dataset."""
        return set([label for image in self.images for label in image.labels])

    @property
    def attributes(self) -> List[TagFrequency]:
        """Return a dataset breakdown by label."""
        label_count: Counter = Counter()
        for image in self.images:
            for label in list(set(image.labels)):
                label_count[label] += 1
        return [
            TagFrequency(tag_name=key, images=label_count[key])
            for key in self.unique_tags
        ]


class ObjectDetectionDataset(Dataset):

    images: List[ObjectDetectionTrainingImage]

    def __init__(self, images=List[ObjectDetectionTrainingImage]):
        self.images = images

    @property
    def attributes(self) -> List[TagFrequency]:
        """Return how many images and how many bounding boxes for each tag."""

        images_count: Counter = Counter()
        bounding_boxes_count: Counter = Counter()

        for image in self.images:
            for tag in self.unique_tags:
                if tag in [region.tag_name for region in image.regions]:
                    images_count[tag] += 1
            for region in image.regions:
                bounding_boxes_count[region.tag_name] += 1

        return [
            TagFrequency(tag_name=key,
                         images=images_count[key],
                         bounding_boxes=bounding_boxes_count[key])
            for key in self.unique_tags
        ]

    @property
    def unique_images(self) -> 'ObjectDetectionDataset':
        return ObjectDetectionDataset(sorted(list(set(self.images))))

    @property
    def unique_tags(self) -> Set[str]:
        """Return the unique tag names present in the dataset."""
        tag_names: List[str] = []
        for image in self.images:
            tag_names.extend(image.unique_tags)
        return set(tag_names)

    @property
    def tagged_images(self) -> 'ObjectDetectionDataset':
        """Returns a new dataset with the tagged images only."""
        return self.__class__(
            images=[image for image in self.images if len(image.regions)])

    def remove_tag(self, tag_to_remove: str) -> None:
        """Remove all instances of a tag in the dataset."""
        if not tag_to_remove in self.unique_tags:
            return None
        for image in self.images:
            image.regions = [
                region for region in image.regions
                if region.tag_name != tag_to_remove
            ]

    def combine_tags(self, tags_to_combine: List[str],
                     new_tag_name: str) -> None:
        """Combine 2 or more tags into a new one."""
        if not any([tag in self.unique_tags for tag in tags_to_combine]):
            return None
        for image in self.images:
            for region in image.regions:
                if region.tag_name in tags_to_combine:
                    region.tag_name = new_tag_name

    def limit_tag_occurrences(self,
                              tag_name: str,
                              max_occurrences: int,
                              impose_on_bounding_boxes: bool = False) -> None:
        """
        Reduce the number of occurrences of a tag.
        """

        # Check that the tag exists in the dataset before doing any work
        if not tag_name in self.unique_tags:
            return None

        tag_frequency: TagFrequency = [
            tag_frequency for tag_frequency in self.attributes
            if tag_frequency.tag_name == tag_name
        ][0]

        if impose_on_bounding_boxes:
            self._limit_bounding_box_occurrences(
                tag_frequency=tag_frequency, max_occurrences=max_occurrences)
        else:
            self._limit_image_occurrences(tag_frequency=tag_frequency,
                                          max_occurrences=max_occurrences)

    def _limit_bounding_box_occurrences(self, tag_frequency: TagFrequency,
                                        max_occurrences: int) -> None:

        if not tag_frequency.bounding_boxes:
            return None
        excess_tags = tag_frequency.bounding_boxes - max_occurrences
        for image in self.images:
            for index in reversed(range(0, len(image.regions))):
                if excess_tags > 0 and image.regions[
                        index].tag_name == tag_frequency.tag_name:
                    del image.regions[index]
                    excess_tags -= 1
                if excess_tags == 0:
                    break

    def _limit_image_occurrences(self, tag_frequency: TagFrequency,
                                 max_occurrences: int) -> None:

        excess_tags = tag_frequency.images - max_occurrences
        for image in self.images:
            if excess_tags > 0 and tag_frequency.tag_name in image.unique_tags:
                for index in reversed(range(0, len(image.regions))):
                    if image.regions[index].tag_name == tag_frequency.tag_name:
                        del image.regions[index]
                excess_tags -= 1
            if excess_tags == 0:
                break
