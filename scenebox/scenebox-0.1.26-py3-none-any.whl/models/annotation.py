#  Copyright (c) 2020 Caliber Data Labs.
#  All rights reserved.
#
from datetime import datetime
from typing import Dict, List, NamedTuple, Optional, Union, Tuple

from ..constants import (AnnotationMediaTypes, AnnotationProviders,
                         AnnotationTypes, TrafficObjectTagging)
from ..custom_exceptions import InvalidAnnotationError
from ..tools import misc, time_utils
from ..tools.logger import get_logger
from .object_access import ObjectAccess

logger = get_logger(__name__)


class Annotation(object):
    def __init__(
            self,
            annotation_meta=None):
        self.id: str = misc.get_guid()
        self.timestamp: datetime = datetime.utcnow()
        self.asset_id: Optional[str] = None
        self.media_type: Optional[str] = None
        self.provider: Optional[str] = None
        self.annotation_type: Optional[str] = None
        self.annotation_entities: List[AnnotationEntity] = []
        self.annotation_meta: Dict = annotation_meta or {}
        self.sets: List[str] = []
        self.session_uid: Optional[str] = None
        self.sensor: Optional[str] = None
        self.version: Optional[str] = None
        self.ground_truth: str = "true"
        self.masks: List[ObjectAccess] = []


    def set_asset_id(self, asset_id: str):
        self.asset_id = asset_id

    def finalize(self):
        self.set_annotation_entities()

        self.__sanity_check()

    def set_annotation_entities(self):
        pass

    def __sanity_check(self):
        if self.annotation_type not in AnnotationTypes.VALID_TYPES:
            raise InvalidAnnotationError(
                "invalid annotation type {}".format(self.annotation_type)
            )

        if self.media_type not in AnnotationMediaTypes.VALID_TYPES:
            raise InvalidAnnotationError(
                "invalid annotation type {}".format(self.media_type)
            )

    def to_dic(self):
        """
        return a dictionary object representative of Annotation
        :return: dictionary object
        """
        annotation_entities_ = []
        labels = set()
        for annotation_entity in self.annotation_entities:
            annotation_entities_.append(annotation_entity.to_dic())
            labels.add(annotation_entity.label)
        return {
            "session_uid": self.session_uid,
            "timestamp": time_utils.datetime_or_str_to_iso_utc(self.timestamp),
            "asset_id": self.asset_id,
            "media_type": self.media_type,
            "provider": self.provider,
            "annotation_type": self.annotation_type,
            "annotation_entities": annotation_entities_,
            "sets": self.sets,
            "labels": list(labels),
            "sensor": self.sensor,
            "version": self.version,
            "ground_truth": self.ground_truth,
            "masks": [_.to_dic() for _ in self.masks]
        }


class RelatedAnnotation(object):
    # initialize a related annotation object(
    def __init__(self, related_annotation_dic):
        try:
            # annotation label
            self.uid = related_annotation_dic["uid"]

            # the unique (worldwide) id of the entity
            self.relationship = related_annotation_dic["relationship"]
            if self.relationship not in {"parent", "child", "sibling"}:
                raise InvalidAnnotationError(
                    "unrecognized relation {}".format(self.relationship)
                )

        except KeyError as e:
            raise InvalidAnnotationError(str(e))

    def to_dic(self):
        """
        return a dictionary object representative of Annotation entity
        :return: dictionary object
        """
        return {"uid": self.uid, "relationship": self.relationship}


class AnnotationEntity(object):
    # initialize an annotation object (a single annotation such as tire,
    # pedestrian, etc)
    def __init__(self,
                 label: str,
                 annotation_type: str,
                 class_name: Optional[str] = None,
                 coordinates: Optional[List] = None,
                 confidence: Optional[float] = None,
                 mask_color: Optional[str] = None,
                 mask_id: Optional[str] = None,
                 uid: Optional[str] = None,
                 category_id: Optional[int] = None,
                 related_annotations: Optional[List[RelatedAnnotation]] = None,
                 attributes: Optional[dict] = None):

        # annotation label
        self.label = label
        self.category_id = category_id
        self.class_name = class_name
        if mask_color:
            self.mask_color = mask_color.lower()
            if not misc.is_valid_hex(self.mask_color):
                raise InvalidAnnotationError(
                    "invalid hex color {}".format(mask_color))
        else:
            self.mask_color = None

        # the unique (worldwide) id of the entity
        self.uid = uid or misc.get_guid()

        self.mask_id = mask_id

        if isinstance(confidence, float):
            self.confidence = confidence
            if self.confidence < 0 or self.confidence > 1:
                raise InvalidAnnotationError(
                    "confidence {} should be between 0 and 1".format(
                        self.confidence))
        elif confidence is None:
            self.confidence = None
        else:
            raise InvalidAnnotationError(
                "invalid confidence format {}".format(type(confidence))
            )

        if annotation_type not in AnnotationTypes.VALID_TYPES:
            raise InvalidAnnotationError(
                "invalid annotation type {}".format(annotation_type)
            )
        else:
            self.annotation_type = annotation_type

        # x, y coordinates
        self.coordinates = []

        for point in coordinates or []:
            self.coordinates.append(
                {"x": float(point["x"]), "y": float(point["y"])})

        # coordinate checks for various geometry types:
        if self.annotation_type == AnnotationTypes.POINT and len(
                self.coordinates) != 1:
            raise InvalidAnnotationError(
                "point annotations should exactly have 1 point"
            )

        if self.annotation_type == AnnotationTypes.TWO_D_BOUNDING_BOX and len(
                self.coordinates) != 4:
            raise InvalidAnnotationError(
                "bounding_box annotations should exactly have 4 points"
            )

        if self.annotation_type in {
                AnnotationTypes.POLYGON,
                AnnotationTypes.LINE} and not self.coordinates:
            raise InvalidAnnotationError(
                "empty coordinates for annotation_type = {}".format(
                    self.annotation_type))

        if self.annotation_type == AnnotationTypes.SEGMENTATION and not self.mask_color:
            raise InvalidAnnotationError(
                "mask color should be specified for segmentation"
            )

        # get all related_annotations
        self.related_annotations = []

        for related_annotation in related_annotations or []:
            self.related_annotations.append(
                RelatedAnnotation(related_annotation))

        # optional attributes of an entity
        self.attributes = attributes or {}

    def to_dic(self):
        """
        return a dictionary object representative of Annotation entity
        :return: dictionary object
        """
        related_annotations_ = []
        for related_annotation in self.related_annotations:
            related_annotations_.append(related_annotation.to_dic())

        dic = {
            "uid": self.uid,
            "label": self.label,
            "annotation_type": self.annotation_type,
            "attributes": self.attributes,
            "coordinates": self.coordinates,
            "related_annotations": related_annotations_,
            "category_id": self.category_id,
            "confidence": self.confidence,
        }
        if self.mask_id:
            dic["mask_id"] = self.mask_id
        if self.mask_color:
            dic["mask_color"] = self.mask_color
        if self.class_name:
            dic["class_name"] = self.class_name
        return dic

    @classmethod
    def from_dict(cls, annotation_entity_dic: dict):

        confidence = annotation_entity_dic.get("confidence")
        if isinstance(confidence, float):
            if confidence < 0 or confidence > 1:
                raise InvalidAnnotationError(
                    "confidence {} should be between 0 and 1".format(
                        confidence))
        elif confidence is None:
            pass
        else:
            raise InvalidAnnotationError(
                "invalid confidence format {}".format(type(confidence))
            )

        coordinates = []

        try:
            for point in annotation_entity_dic.get("coordinates", []):
                coordinates.append(
                    {"x": float(point["x"]), "y": float(point["y"])})

        except KeyError:
            raise InvalidAnnotationError(str(KeyError))

        related_annotations = []
        for related_annotation in annotation_entity_dic.get(
                "related_annotations", []):
            related_annotations.append(RelatedAnnotation(related_annotation))

        return cls(
            label=annotation_entity_dic["label"],
            category_id=annotation_entity_dic.get(
                "category_id"),
            uid=annotation_entity_dic.get("uid", misc.get_guid()),
            annotation_type=annotation_entity_dic["annotation_type"],
            mask_id=annotation_entity_dic.get("mask_id"),
            confidence=confidence,
            mask_color=annotation_entity_dic.get("mask_color"),
            coordinates=coordinates,
            attributes=annotation_entity_dic.get("attributes"),
            class_name=annotation_entity_dic.get("class_name"),
            related_annotations=related_annotations
        )


class SegmentationAnnotation(Annotation):
    def __init__(self,
                 labels: List[str],
                 mask_colors: List[str],
                 provider: str,
                 image_id: Optional[str] = None,
                 mask_urls: Optional[List[str]] = None,
                 mask_uris: Optional[List[str]] = None,
                 mask_ids: Optional[List[str]] = None,
                 id: Optional[str] = None,
                 version: Optional[str] = None,
                 confidences: Optional[List[float]] = None,
                 set_id: Optional[str] = None,
                 ground_truth: bool = True):
        super().__init__()
        if id:
            self.id = id
        self.asset_id = image_id
        if set_id:
            self.sets = [set_id]
        self.annotation_type = AnnotationTypes.SEGMENTATION
        self.media_type = AnnotationMediaTypes.IMAGE
        self.ground_truth = "true" if ground_truth else "false"
        self.labels = labels
        self.mask_urls = mask_urls or [None] * len(labels)
        self.mask_uris = mask_uris or [None] * len(labels)
        self.mask_ids = mask_ids or [None] * len(labels)
        self.mask_colors = mask_colors
        self.provider = provider
        self.version = version
        self.confidences = confidences or [None] * len(labels)
        self.finalize()

    def set_annotation_entities(self):
        self.annotation_entities = []
        assert len(self.labels) == len(self.mask_urls)
        assert len(self.labels) == len(self.confidences)
        assert len(self.labels) == len(self.mask_colors)
        assert len(self.labels) == len(self.mask_uris)
        assert len(self.labels) == len(self.mask_ids)
        masks = set()
        for label, url, confidence, mask_color, uri, mask_id in zip(
                self.labels, self.mask_urls, self.confidences, self.mask_colors, self.mask_uris, self.mask_ids):
            if url:
                object_access = ObjectAccess(url=url)
            elif uri:
                object_access = ObjectAccess(uri=uri)
            elif mask_id:
                object_access = ObjectAccess(id=mask_id)
            else:
                raise InvalidAnnotationError(
                    "either url or uri should be specified for {}".format(
                        self.id))

            masks.add(object_access)
            self.annotation_entities.append(
                AnnotationEntity(
                    label=label,
                    annotation_type=AnnotationTypes.SEGMENTATION,
                    mask_id=object_access.id,
                    confidence=confidence,
                    mask_color=mask_color
                )
            )
            self.masks = list(masks)


class MRCNNAnnotation(Annotation):
    def __init__(
        self,
        media_asset_id: str,
        file_labels: dict,
        annotation_binary_id: str,
        id: Optional[str] = None,
        version: Optional[str] = None,
        destination_set: Optional[str] = None
    ):
        super().__init__()

        if id:
            self.id = id

        if destination_set:
            self.sets = [destination_set]

        self.annotation_meta = {
            "binary_id": annotation_binary_id
        }

        self.inference_labelling_model = TrafficObjectTagging.MRCNN
        self.provider = "mrcnn_bbox"
        self.file_labels = file_labels
        self.version = version
        self.ground_truth = "false"
        self.asset_id = media_asset_id
        self.media_type = AnnotationMediaTypes.IMAGE
        self.annotation_type = AnnotationTypes.TWO_D_BOUNDING_BOX
        self.finalize()

    def set_annotation_entities(self):
        try:
            if "bounding_boxes" in self.file_labels:
                bounding_box_array = self.file_labels["bounding_boxes"]
                bounding_box_list = bounding_box_array.tolist()
                for i, bb in enumerate(bounding_box_list):
                    label = self.file_labels["labels"][i]
                    confidence = float(
                        self.file_labels["confidences"][i])
                    self.set_bounding_box_annotation_entities(
                        bb, label, confidence)
            # TODO: What to do with masks?
            # if 'masks' in self.inference_label_response:
            #     for i, mask_array in enumerate(self.inference_label_response['masks']):
            #         label = self.inference_label_response['class_labels'][i]
            #         self.set_mask_annotation_entities(mask_array, label)
        except Exception as e:
            logger.error("Could not set annotation entity::: {}".format(e))

    def set_bounding_box_annotation_entities(
            self, bb: List[Union[int, float]], label: str, confidence: float):
        """
        Note: box is an array of 4 numbers representing a 2D bounding box. The first two numbers are the x, y
        coordinates of the top left corner of the box. 3rd and 4th numbers represent length of box
        along x and y axes. Coordinate system has origin at the top left corner of the image.
        """
        # MRCNN ROIs are of form::: [y1, x1, y2, x2] with image coordinates
        y1, x1, y2, x2 = bb
        try:
            left = float(x1)
            top = float(y1)
            width = float(x2 - x1)
            height = float(y2 - y1)
        except KeyError as e:
            raise InvalidAnnotationError(str(e))
        key = "{}_{}".format(self.id, label)

        coordinates = [
            {"x": left, "y": top},
            {"x": left + width, "y": top},
            {"x": left + width, "y": top + height},
            {"x": left, "y": top + height},
        ]
        self.annotation_entities.append(
            AnnotationEntity(
                label=label,
                annotation_type=AnnotationTypes.TWO_D_BOUNDING_BOX,
                coordinates=coordinates,
                confidence=confidence
            )
        )

    def set_mask_annotation_entities(self, mask_array, label):
        # TODO (Jon): Support instance segmentation with masks!!
        raise NotImplementedError


class BoundingBox(NamedTuple):
    x_min: float
    x_max: float
    y_min: float
    y_max: float
    label: str
    category_id: Optional[int] = None
    confidence: Optional[float] = None


class BoundingBoxAnnotation(Annotation):
    def __init__(self,
                 provider: str,
                 bounding_boxes: List[BoundingBox],
                 image_id: Optional[str] = None,
                 id: Optional[str] = None,
                 version: Optional[str] = None,
                 set_id: Optional[str] = None,
                 ground_truth: bool = True):
        super().__init__()
        if id:
            self.id = id
        self.asset_id = image_id
        if set_id:
            self.sets = [set_id]
        self.annotation_type = AnnotationTypes.TWO_D_BOUNDING_BOX
        self.media_type = AnnotationMediaTypes.IMAGE
        self.ground_truth = "true" if ground_truth else "false"
        self.provider = provider
        self.version = version
        self.bounding_boxes = bounding_boxes
        self.finalize()

    def set_annotation_entities(self):
        self.annotation_entities = []

        if not isinstance(self.bounding_boxes, list):
            raise InvalidAnnotationError(
                "bounding box annotation is expected to be list"
            )

        for bounding_box in self.bounding_boxes:
            try:
                category_id = bounding_box.category_id
                left = float(bounding_box.x_min)
                top = float(bounding_box.y_max)
                bottom = float(bounding_box.y_min)
                right = float(bounding_box.x_max)
            except KeyError as e:
                raise InvalidAnnotationError(str(e))

            coordinates = [
                {"x": left, "y": bottom},
                {"x": right, "y": bottom},
                {"x": right, "y": top},
                {"x": left, "y": top},
            ]
            self.annotation_entities.append(
                AnnotationEntity(
                    label=bounding_box.label,
                    category_id=category_id,
                    annotation_type=AnnotationTypes.TWO_D_BOUNDING_BOX,
                    coordinates=coordinates,
                    confidence=bounding_box.confidence
                )
            )


class Polygon(NamedTuple):
    coordinates: List[Tuple[float,float]]
    label: str
    category_id: Optional[int] = None
    confidence: Optional[float] = None


class PolygonAnnotation(Annotation):
    def __init__(self,
                 provider: str,
                 polygons: List[Polygon],
                 image_id: Optional[str] = None,
                 id: Optional[str] = None,
                 version: Optional[str] = None,
                 set_id: Optional[str] = None,
                 ground_truth: bool = True):
        super().__init__()
        if id:
            self.id = id
        self.asset_id = image_id
        if set_id:
            self.sets = [set_id]
        self.annotation_type = AnnotationTypes.POLYGON
        self.media_type = AnnotationMediaTypes.IMAGE
        self.ground_truth = "true" if ground_truth else "false"
        self.provider = provider
        self.version = version
        self.polygons = polygons
        self.finalize()

    def set_annotation_entities(self):
        self.annotation_entities = []

        if not isinstance(self.polygons, list):
            raise InvalidAnnotationError(
                "polygon annotation is expected to be list"
            )

        for polygon in self.polygons:
            try:
                category_id = polygon.category_id
                coords_ = polygon.coordinates
            except KeyError as e:
                raise InvalidAnnotationError(str(e))

            coordinates = []
            for c in coords_:
                coordinates.append({"x": c[0], "y": c[1]})
            self.annotation_entities.append(
                AnnotationEntity(
                    label=polygon.label,
                    category_id=category_id,
                    annotation_type=AnnotationTypes.POLYGON,
                    coordinates=coordinates,
                    confidence=polygon.confidence
                )
            )


class Label(NamedTuple):
    label: str
    class_name: Optional[str] = None
    category_id: Optional[int] = None
    confidence: Optional[float] = None


class ClassificationAnnotation(Annotation):
    def __init__(self,
                 provider: str,
                 labels: List[Label],
                 asset_id: Optional[str] = None,
                 media_type: Optional[str] = AnnotationMediaTypes.IMAGE,
                 id: Optional[str] = None,
                 version: Optional[str] = None,
                 set_id: Optional[str] = None,
                 ground_truth: bool = True):
        super().__init__()
        if id:
            self.id = id
        self.asset_id = asset_id
        if set_id:
            self.sets = [set_id]
        self.annotation_type = AnnotationTypes.CLASSIFICATION
        self.labels = labels
        self.media_type = media_type
        self.ground_truth = "true" if ground_truth else "false"
        self.provider = provider
        self.version = version
        self.finalize()

    def set_annotation_entities(self):
        self.annotation_entities = []
        for label in self.labels:
            self.annotation_entities.append(
                AnnotationEntity(
                    label=label.label,
                    category_id=label.category_id,
                    class_name=label.class_name,
                    annotation_type=AnnotationTypes.CLASSIFICATION,
                    confidence=label.confidence
                )
            )
