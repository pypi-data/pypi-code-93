"""labels.py
============
The label set classes.
"""

import datetime
import json
from io import IOBase
from tempfile import NamedTemporaryFile
import pyarrow as pa
import numpy as np
import pandas as pd
from typing import Any, Optional, Union, Callable, List, Dict, Tuple, Set, IO, cast
from typing_extensions import Literal


from .util import (
    _is_one_gb_available,
    add_object_user_attrs,
    create_temp_directory,
    mark_temp_directory_complete,
    POLYGON_VERTICES_KEYS,
    KEYPOINT_KEYS,
    MAX_FRAMES_PER_BATCH,
    InferenceEntryDict,
    FrameEmbeddingDict,
    CropEmbeddingDict,
    LabelType,
    InferenceFrameSummary,
    LabelFrameSummary,
    BaseLabelEntryDict,
)

CustomMetricsEntry = Union[float, List[List[Union[float, int]]]]
CropType = Literal["GT", "Inference"]


class BaseLabelSet:
    """A frame containing inferences from an experiment.

    Args:
        frame_id (str): A unique id for this frame.
    """

    # TODO: Is this the most pythonic pattern?
    frame_id: str
    crop_type: CropType
    label_data: List[BaseLabelEntryDict]
    _label_ids_set: Set[str]
    crop_embeddings: List[CropEmbeddingDict]

    def __init__(self, *, frame_id: str, crop_type: CropType) -> None:
        if not isinstance(frame_id, str):
            raise Exception("frame ids must be strings")

        if "/" in frame_id:
            raise Exception("frame ids cannot contain slashes (/)")

        self.frame_id = frame_id
        self.crop_type = crop_type
        self.label_data = []
        self.crop_embeddings = []
        self._label_ids_set = set()

    def add_crop_embedding(
        self, *, label_id: str, embedding: List[float], model_id: str = ""
    ) -> None:
        """Add a per inference crop embedding

        Args:
            label_id (str): [description]
            embedding (List[float]): A vector of floats between length 0 and 12,000.
            model_id (str, optional): The model id used to generate these embeddings. Defaults to "".
        """
        if not embedding or len(embedding) > 12000:
            raise Exception("Length of embeddings should be between 0 and 12,000")

        # TODO: check label id present
        self.crop_embeddings.append(
            {
                "uuid": label_id,
                "embedding": embedding,
                "model_id": model_id,
                "date_generated": str(datetime.datetime.now()),
            }
        )

    def _all_label_classes(self) -> List[str]:
        return list(
            set(
                [data["label"] for data in self.label_data if data["label"] != "__mask"]
            )
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert this label set into a dictionary representation.

        Returns:
            dict: dictified frame
        """
        row = {
            "task_id": self.frame_id,
            "label_data": self.label_data,
            "type": self.crop_type,
        }

        return row

    def _to_summary(self) -> LabelFrameSummary:
        """Converts this frame to a lightweight summary dict for internal cataloging

        Returns:
            dict: lightweight summaried frame
        """
        label_counts: Dict[LabelType, int] = {}
        for label in self.label_data:
            if not label_counts.get(label["label_type"]):
                label_counts[label["label_type"]] = 0
            label_counts[label["label_type"]] += 1

        return {
            "frame_id": self.frame_id,
            "label_counts": label_counts,
        }

    # Handle confidence
    def add_2d_line_segment(
        self,
        *,
        sensor_id: str,
        label_id: str,
        classification: str,
        x1: Union[int, float],
        y1: Union[int, float],
        x2: Union[int, float],
        y2: Union[int, float],
        confidence: Optional[float] = None,
        iscrowd: Optional[bool] = None,
        user_attrs: Optional[Dict[str, Any]] = None,
        links: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add a 2D line segment.

        Args:
            sensor_id (str): sensor_id
            label_id (str): label_id which is unique across datasets and inferences.
            classification (str): the classification string
            x1 (int or float): The x-coord of the first vertex in pixels
            y1 (int or float): The x-coord of the first vertex in pixels
            x2 (int or float): The x-coord of the first vertex in pixels
            y2 (int or float): The x-coord of the first vertex in pixels
            confidence (float): The confidence between 0.0 and 1.0 of the prediction
            iscrowd (bool, optional): Is this label marked as a crowd. Defaults to None.
            user_attrs (dict, optional): Any additional label-level metadata fields. Defaults to None.
        """

        if not isinstance(label_id, str):
            raise Exception("label ids must be strings")
        if "/" in label_id:
            raise Exception("label ids cannot contain slashes (/)")

        if not isinstance(classification, str):
            raise Exception("classifications must be strings")

        attrs = {"x1": x1, "y1": y1, "x2": x2, "y2": y2}

        if confidence is not None:
            if not isinstance(confidence, float):
                raise Exception("confidence must be floats")
            if confidence < 0.0 or confidence > 1.0:
                raise Exception("confidence must be between 0.0 and 1.0")

            attrs["confidence"] = confidence

        if iscrowd is not None:
            attrs["iscrowd"] = iscrowd

        if links is not None:
            for k, v in links.items():
                if "link__" not in k:
                    k = "link__" + k
                attrs[k] = v

        add_object_user_attrs(attrs, user_attrs)

        self.label_data.append(
            {
                "uuid": label_id,
                "linked_labels": [],
                "label_type": "LINE_SEGMENT_2D",
                "label": classification,
                "label_coordinate_frame": sensor_id,
                "attributes": attrs,
            }
        )
        self._label_ids_set.add(label_id)

    def add_2d_bbox(
        self,
        *,
        sensor_id: str,
        label_id: str,
        classification: str,
        top: Union[int, float],
        left: Union[int, float],
        width: Union[int, float],
        height: Union[int, float],
        confidence: Optional[float] = None,
        area: Optional[float] = None,
        iscrowd: Optional[bool] = None,
        user_attrs: Optional[Dict[str, Any]] = None,
        links: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add a 2D bounding box.

        Args:
            sensor_id (str): sensor_id
            label_id (str): label_id which is unique across datasets and inferences.
            classification (str): the classification string
            top (int or float): The top of the box in pixels
            left (int or float): The left of the box in pixels
            width (int or float): The width of the box in pixels
            height (int or float): The height of the box in pixels
            confidence (float): The confidence between 0.0 and 1.0 of the prediction
            area (float, optional): The area of the image.
            iscrowd (bool, optional): Is this label marked as a crowd. Defaults to None.
            user_attrs (dict, optional): Any additional label-level metadata fields. Defaults to None.
        """

        if not isinstance(label_id, str):
            raise Exception("label ids must be strings")
        if "/" in label_id:
            raise Exception("label ids cannot contain slashes (/)")

        if not isinstance(classification, str):
            raise Exception("classifications must be strings")

        attrs = {
            "top": top,
            "left": left,
            "width": width,
            "height": height,
        }

        if confidence is not None:
            if not isinstance(confidence, float):
                raise Exception("confidence must be floats")
            if confidence < 0.0 or confidence > 1.0:
                raise Exception("confidence must be between 0.0 and 1.0")

            attrs["confidence"] = confidence

        if iscrowd is not None:
            attrs["iscrowd"] = iscrowd
        # TODO: This is mostly legacy for vergesense
        if area is not None:
            attrs["area"] = area

        if links is not None:
            for k, v in links.items():
                if "link__" not in k:
                    k = "link__" + k
                attrs[k] = v

        add_object_user_attrs(attrs, user_attrs)

        self.label_data.append(
            {
                "uuid": label_id,
                "linked_labels": [],
                "label_type": "BBOX_2D",
                "label": classification,
                "label_coordinate_frame": sensor_id,
                "attributes": attrs,
            }
        )
        self._label_ids_set.add(label_id)

    def add_text_token(
        self,
        *,
        sensor_id: str,
        label_id: str,
        index: int,
        token: str,
        classification: str,
        visible: bool,
        confidence: Optional[float] = None,
        user_attrs: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add a label for a text token.

        Args:
            sensor_id (str): sensor_id
            label_id (str): label_id which is unique across datasets and inferences.
            index (int): the index of this token in the text
            token (str): the text content of this token
            classification (str): the classification string
            visible (bool): is this a visible token in the text
            confidence (float): confidence of prediction
            user_attrs (dict, optional): Any additional label-level metadata fields. Defaults to None.
        """
        if not isinstance(label_id, str):
            raise Exception("label ids must be strings")
        if "/" in label_id:
            raise Exception("label ids cannot contain slashes (/)")

        if not isinstance(classification, str):
            raise Exception("classifications must be strings")

        attrs = {
            "index": index,
            "token": token,
            "visible": visible,
        }

        if confidence is not None:
            if not isinstance(confidence, float):
                raise Exception("confidence must be floats")
            if confidence < 0.0 or confidence > 1.0:
                raise Exception("confidence must be between 0.0 and 1.0")

            attrs["confidence"] = confidence

        add_object_user_attrs(attrs, user_attrs)

        self.label_data.append(
            {
                "uuid": label_id,
                "linked_labels": [],
                "label_type": "TEXT_TOKEN",
                "label": classification,
                "label_coordinate_frame": sensor_id,
                "attributes": attrs,
            }
        )
        self._label_ids_set.add(label_id)

    def add_3d_cuboid(
        self,
        *,
        label_id: str,
        classification: str,
        position: List[float],
        dimensions: List[float],
        rotation: List[float],
        confidence: Optional[float] = None,
        iscrowd: Optional[bool] = None,
        user_attrs: Optional[Dict[str, Any]] = None,
        links: Optional[Dict[str, Any]] = None,
        coord_frame_id: Optional[str] = None,
    ) -> None:
        """Add an inference for a 3D cuboid.

        Args:
            label_id (str): label_id which is unique across datasets and inferences.
            classification (str): the classification string
            position (list of float): the position of the center of the cuboid
            dimensions (list of float): the dimensions of the cuboid
            rotation (list of float): the local rotation of the cuboid, represented as an xyzw quaternion.
            confidence (float): confidence of prediction
            iscrowd (bool, optional): Is this label marked as a crowd. Defaults to None.
            user_attrs (dict, optional): Any additional label-level metadata fields. Defaults to None.
            links (dict, optional): Links between labels. Defaults to None.
            coord_frame_id (str, optional): Coordinate frame id. Defaults to 'world'
        """
        if coord_frame_id is None:
            coord_frame_id = "world"

        if not isinstance(label_id, str):
            raise Exception("label ids must be strings")
        if "/" in label_id:
            raise Exception("label ids cannot contain slashes (/)")

        if not isinstance(classification, str):
            raise Exception("classifications must be strings")

        attrs: Dict[str, Any] = {
            "pos_x": position[0],
            "pos_y": position[1],
            "pos_z": position[2],
            "dim_x": dimensions[0],
            "dim_y": dimensions[1],
            "dim_z": dimensions[2],
            "rot_x": rotation[0],
            "rot_y": rotation[1],
            "rot_z": rotation[2],
            "rot_w": rotation[3],
        }

        if confidence is not None:
            if not isinstance(confidence, float):
                raise Exception("confidence must be floats")
            if confidence < 0.0 or confidence > 1.0:
                raise Exception("confidence must be between 0.0 and 1.0")

            attrs["confidence"] = confidence

        if iscrowd is not None:
            attrs["iscrowd"] = iscrowd

        add_object_user_attrs(attrs, user_attrs)

        if links is not None:
            for k, v in links.items():
                if "link__" not in k:
                    k = "link__" + k
                attrs[k] = v

        self.label_data.append(
            {
                "uuid": label_id,
                "linked_labels": [],
                "label_type": "CUBOID_3D",
                "label": classification,
                "label_coordinate_frame": coord_frame_id,
                "attributes": attrs,
            }
        )
        self._label_ids_set.add(label_id)

    def add_2d_keypoints(
        self,
        *,
        sensor_id: str,
        label_id: str,
        classification: str,
        top: Union[int, float],
        left: Union[int, float],
        width: Union[int, float],
        height: Union[int, float],
        keypoints: List[Dict[KEYPOINT_KEYS, Union[int, float, str]]],
        confidence: Optional[float] = None,
        user_attrs: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add an inference for a 2D keypoints task.

        A keypoint is a dictionary of the form:
            'x': x-coordinate in pixels
            'y': y-coordinate in pixels
            'name': string name of the keypoint

        Args:
            sensor_id (str): sensor_id
            label_id (str): label_id which is unique across datasets and inferences.
            classification (str): the classification string
            top (int or float): The top of the box in pixels
            left (int or float): The left of the box in pixels
            width (int or float): The width of the box in pixels
            height (int or float): The height of the box in pixels
            keypoints (list of dicts): The keypoints of this detection
            confidence (float): The confidence between 0.0 and 1.0 of the prediction
            user_attrs (dict, optional): Any additional label-level metadata fields. Defaults to None.
        """

        if not isinstance(label_id, str):
            raise Exception("label ids must be strings")
        if "/" in label_id:
            raise Exception("label ids cannot contain slashes (/)")

        if not isinstance(classification, str):
            raise Exception("classifications must be strings")

        attrs = {
            "top": top,
            "left": left,
            "width": width,
            "height": height,
            "keypoints": keypoints,
        }

        if confidence is not None:
            if not isinstance(confidence, float):
                raise Exception("confidence must be floats")
            if confidence < 0.0 or confidence > 1.0:
                raise Exception("confidence must be between 0.0 and 1.0")

            attrs["confidence"] = confidence

        add_object_user_attrs(attrs, user_attrs)

        self.label_data.append(
            {
                "uuid": label_id,
                "linked_labels": [],
                "label_type": "KEYPOINTS_2D",
                "label": classification,
                "label_coordinate_frame": sensor_id,
                "attributes": attrs,
            }
        )
        self._label_ids_set.add(label_id)

    def add_2d_polygon_list(
        self,
        *,
        sensor_id: str,
        label_id: str,
        classification: str,
        polygons: List[Dict[POLYGON_VERTICES_KEYS, List[Tuple[Union[int, float]]]]],
        confidence: Optional[float] = None,
        center: Optional[List[Union[int, float]]] = None,
        user_attrs: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add an inference for a 2D polygon list instance segmentation task.

        Polygons are dictionaries of the form:
            'vertices': List of (x, y) vertices (e.g. [[x1,y1], [x2,y2], ...])
                The polygon does not need to be closed with (x1, y1).
                As an example, a bounding box in polygon representation would look like:

                .. code-block::

                    {
                        'vertices': [
                            [left, top],
                            [left + width, top],
                            [left + width, top + height],
                            [left, top + height]
                        ]
                    }


        Args:
            sensor_id (str): sensor_id
            label_id (str): label_id which is unique across datasets and inferences.
            classification (str): the classification string
            polygons (list of dicts): The polygon geometry
            confidence (float): The confidence between 0.0 and 1.0 of the prediction
            center (list of ints or floats, optional): The center point of the instance
            user_attrs (dict, optional): Any additional label-level metadata fields. Defaults to None.
        """

        if not isinstance(label_id, str):
            raise Exception("label ids must be strings")
        if "/" in label_id:
            raise Exception("label ids cannot contain slashes (/)")

        if not isinstance(classification, str):
            raise Exception("classifications must be strings")

        attrs: Dict[str, Any] = {"polygons": polygons, "center": center}

        if confidence is not None:
            if not isinstance(confidence, float):
                raise Exception("confidence must be floats")
            if confidence < 0.0 or confidence > 1.0:
                raise Exception("confidence must be between 0.0 and 1.0")

            attrs["confidence"] = confidence

        add_object_user_attrs(attrs, user_attrs)

        self.label_data.append(
            {
                "uuid": label_id,
                "linked_labels": [],
                "label_type": "POLYGON_LIST_2D",
                "label": classification,
                "label_coordinate_frame": sensor_id,
                "attributes": attrs,
            }
        )
        self._label_ids_set.add(label_id)

    def add_2d_semseg(self, *, sensor_id: str, label_id: str, mask_url: str) -> None:
        """Add an inference for 2D semseg.

        Args:
            sensor_id (str): sensor_id
            label_id (str): label_id which is unique across datasets and inferences.
            mask_url (str): URL to the pixel mask png.
        """

        if not isinstance(label_id, str):
            raise Exception("label ids must be strings")
        if "/" in label_id:
            raise Exception("label ids cannot contain slashes (/)")

        self.label_data.append(
            {
                "uuid": label_id,
                "linked_labels": [],
                "label": "__mask",
                "label_coordinate_frame": sensor_id,
                "label_type": "SEMANTIC_LABEL_URL_2D",
                "attributes": {"url": mask_url},
            }
        )
        self._label_ids_set.add(label_id)

    def add_2d_classification(
        self,
        *,
        sensor_id: str,
        label_id: str,
        classification: str,
        confidence: Optional[float] = None,
        user_attrs: Optional[Dict[str, Any]] = None,
        secondary_labels: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add an inference for 2D classification.

        Args:
            sensor_id (str): sensor_id
            label_id (str): label_id which is unique across datasets and inferences.
            classification (str): the classification string
            confidence (float): The confidence between 0.0 and 1.0 of the prediction
            user_attrs (dict, optional): Any additional label-level metadata fields. Defaults to None.
        """

        if not isinstance(label_id, str):
            raise Exception("label ids must be strings")
        if "/" in label_id:
            raise Exception("label ids cannot contain slashes (/)")

        if not isinstance(classification, str):
            raise Exception("classifications must be strings")

        attrs = {}

        if confidence is not None:
            if not isinstance(confidence, float):
                raise Exception("confidence must be floats")
            if confidence < 0.0 or confidence > 1.0:
                raise Exception("confidence must be between 0.0 and 1.0")

            attrs["confidence"] = confidence

        if secondary_labels is not None:
            for k, v in secondary_labels.items():
                attrs[k] = v

        add_object_user_attrs(attrs, user_attrs)

        self.label_data.append(
            {
                "uuid": label_id,
                "linked_labels": [],
                "label_type": "CLASSIFICATION_2D",
                "label": classification,
                "label_coordinate_frame": sensor_id,
                "attributes": attrs,
            }
        )
        self._label_ids_set.add(label_id)

    def add_3d_classification(
        self,
        *,
        label_id: str,
        classification: str,
        confidence: Optional[float] = None,
        coord_frame_id: Optional[str] = None,
        user_attrs: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add a label for 3D classification.

        Args:
            label_id (str): label_id which is unique across datasets and inferences.
            classification (str): the classification string
            confidence (float): The confidence between 0.0 and 1.0 of the prediction
            coord_frame_id (optional, str): The coordinate frame id.
            user_attrs (dict, optional): Any additional label-level metadata fields. Defaults to None.
        """

        if coord_frame_id is None:
            coord_frame_id = "world"

        if not isinstance(label_id, str):
            raise Exception("label ids must be strings")
        if "/" in label_id:
            raise Exception("label ids cannot contain slashes (/)")

        if not isinstance(classification, str):
            raise Exception("classifications must be strings")

        attrs = {}

        if confidence is not None:
            if not isinstance(confidence, float):
                raise Exception("confidence must be floats")
            if confidence < 0.0 or confidence > 1.0:
                raise Exception("confidence must be between 0.0 and 1.0")

            attrs["confidence"] = confidence

        add_object_user_attrs(attrs, user_attrs)

        self.label_data.append(
            {
                "uuid": label_id,
                "linked_labels": [],
                "label_type": "CLASSIFICATION_3D",
                "label": classification,
                "label_coordinate_frame": coord_frame_id,
                "attributes": attrs,
            }
        )
        self._label_ids_set.add(label_id)


class InferenceLabelSet(BaseLabelSet):
    custom_metrics: Dict[str, CustomMetricsEntry]
    visualization_assets: Dict[str, str]

    def __init__(self, *, frame_id: str) -> None:
        super().__init__(frame_id=frame_id, crop_type="Inference")
        self.custom_metrics = {}
        self.visualization_assets = {}

    def add_custom_metric(self, name: str, value: CustomMetricsEntry) -> None:
        """Add a custom metric for a given inference frame.

        Args:
            name (str): The name of the custom metric being added. Must match one of the custom_metrics already defined by the corresponding Project.
            value (Union[float, List[Union[int, float]]]): The value of the custom metric (either a float or 2d list of floats/integers).
        """
        if not (isinstance(value, float) or isinstance(value, list)):
            raise Exception(
                "Custom metrics values must be either a float, or a 2D list of floats/integers."
            )

        self.custom_metrics[name] = value

    def add_visualization_asset(self, image_id: str, image_url: str) -> None:
        self.visualization_assets[image_id] = image_url

    def to_dict(self) -> Dict[str, Any]:
        row = super().to_dict()

        row["custom_metrics"] = self.custom_metrics
        row["inference_metadata"] = {"visualization_assets": self.visualization_assets}
        row["inference_data"] = row["label_data"]
        del row["label_data"]

        return row

    def _to_summary(self) -> InferenceFrameSummary:
        """Converts this frame to a lightweight summary dict for internal cataloging

        Returns:
            dict: lightweight summaried frame
        """
        result: Any = super()._to_summary()
        result["custom_metrics_names"] = list(self.custom_metrics.keys())
        return result


class GTLabelSet(BaseLabelSet):
    def __init__(self, *, frame_id: str) -> None:
        super().__init__(frame_id=frame_id, crop_type="GT")


class UpdateGTLabelSet(GTLabelSet):
    is_snapshot: bool

    def __init__(self, *, frame_id: str, is_snapshot: Optional[bool] = True) -> None:
        super().__init__(frame_id=frame_id)
        self.is_snapshot = True

    def to_dict(self) -> Dict[str, Any]:
        if self.is_snapshot:
            return super().to_dict()
        else:
            raise Exception("Not Implemented")


class UpdateInferenceLabelSet(InferenceLabelSet):
    is_snapshot: bool

    def __init__(self, *, frame_id: str, is_snapshot: Optional[bool] = True) -> None:
        super().__init__(frame_id=frame_id)
        self.is_snapshot = True

    def to_dict(self) -> Dict[str, Any]:
        if self.is_snapshot:
            return super().to_dict()
        else:
            raise Exception("Not Implemented")


# class Frame:

# class LabeledFrame:


# class FrameEmbedding:

# class CropEmbedding:
