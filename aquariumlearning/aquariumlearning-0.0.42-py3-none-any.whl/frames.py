"""frames.py
============
The base frame and update frame classes.
"""

import datetime
import json
import numbers
from io import IOBase
from tempfile import NamedTemporaryFile
import pyarrow as pa
import numpy as np
import pandas as pd
import re
from typing import Any, Optional, Union, Callable, List, Dict, Tuple, Set, IO, cast
from typing_extensions import Protocol, TypedDict

from .util import (
    _is_one_gb_available,
    assert_valid_name,
    add_object_user_attrs,
    create_temp_directory,
    mark_temp_directory_complete,
    TYPE_PRIMITIVE_TO_STRING_MAP,
    USER_METADATA_SEQUENCE,
    USER_METADATA_PRIMITIVE_TYPES,
    USER_METADATA_MODE_TYPES,
    SUPPORTED_USER_METADATA_TYPES,
    POLYGON_VERTICES_KEYS,
    POSITION_KEYS,
    ORIENTATION_KEYS,
    KEYPOINT_KEYS,
    MAX_FRAMES_PER_BATCH,
    GtLabelEntryDict,
    FrameEmbeddingDict,
    CropEmbeddingDict,
    LabelType,
    LabelFrameSummary,
    InferenceFrameSummary,
    UpdateType,
)

from .labels import GTLabelSet, InferenceLabelSet

# TODO: optional types aren't supported in python, so we should avoid it
# TODO: Give these explicit, concrete typing
CoordinateFrameDict = Dict[str, Any]
SensorDataDict = Dict[str, Any]
GeoDataDict = Dict[str, Any]
UserMetadataEntry = Tuple[
    str,
    SUPPORTED_USER_METADATA_TYPES,
    USER_METADATA_PRIMITIVE_TYPES,
    USER_METADATA_MODE_TYPES,
]


# TODO: handle diffs?
class BaseFrame:
    """A labeled frame for a dataset.

    Args:
        frame_id (str): A unique id for this frame.
        date_captured (str, optional): ISO formatted datetime string. Defaults to None.
        device_id (str, optional): The device that generated this frame. Defaults to None.
    """

    device_id: str
    date_captured: str
    frame_id: str
    coordinate_frames: List[CoordinateFrameDict]
    sensor_data: List[SensorDataDict]
    geo_data: GeoDataDict
    user_metadata: List[UserMetadataEntry]
    _coord_frame_ids_set: Set[str]
    embedding: Optional[FrameEmbeddingDict]
    _label_ids_set: Set[str]

    def __init__(
        self,
        *,
        frame_id: str,
        date_captured: Optional[str] = None,
        device_id: Optional[str] = None,
    ) -> None:
        if not isinstance(frame_id, str):
            raise Exception("frame ids must be strings")

        if "/" in frame_id:
            raise Exception("frame ids cannot contain slashes (/)")

        self.frame_id = frame_id

        if date_captured is not None:
            self.date_captured = date_captured
        else:
            self.date_captured = str(datetime.datetime.now())

        if device_id is not None:
            self.device_id = device_id
        else:
            self.device_id = "default_device"

        self.coordinate_frames = []
        self.sensor_data = []
        self.geo_data = {}
        self.user_metadata = []
        self.embedding = None

        self._coord_frame_ids_set = set()
        self._label_ids_set = set()

    def _add_coordinate_frame(self, coord_frame_obj: Dict[str, str]) -> None:
        """Add coordinate frame to the dataset frame

        Args:
            coord_frame_obj (Dict[str, str]): takes in 'coordinate_frame_id', 'coordinate_frame_type' and optional 'coordinate_frame_metadata'(json dict)
        """
        self.coordinate_frames.append(coord_frame_obj)
        self._coord_frame_ids_set.add(coord_frame_obj["coordinate_frame_id"])

    def _coord_frame_exists(self, coord_frame_id: str) -> bool:
        """Check to see if the coord frame id is already part of the frame

        Args:
            coord_frame_id (str): The coord frame id to check for inclusion

        Returns:
            bool: whether or not the coord frame id is in the frame set
        """
        return coord_frame_id in self._coord_frame_ids_set

    def add_frame_embedding(
        self, *, embedding: List[float], model_id: str = ""
    ) -> None:
        """Add an embedding to this frame

        Args:
            embedding (List[float]): A vector of floats between length 0 and 12,000.
            model_id (str, optional): The model id used to generate these embeddings. Defaults to "".
        """
        if not embedding or len(embedding) > 12000:
            raise Exception("Length of embeddings should be between 0 and 12,000")

        for embedding_el in embedding:
            if not isinstance(embedding_el, numbers.Number):
                raise Exception(
                    f"Unexpectedly encountered a {type(embedding[0])} element. Only flat arrays of numbers are supported for embeddings."
                )

        if not self.embedding:
            self.embedding = {
                "task_id": self.frame_id,
                "model_id": model_id,
                "date_generated": str(datetime.datetime.now()),
                "embedding": embedding,
            }

    def add_user_metadata(
        self,
        key: str,
        val: Union[str, int, float, bool],
        val_type: Optional[USER_METADATA_PRIMITIVE_TYPES] = None,
    ) -> None:
        """Add a user provided metadata field.

        The types of these metadata fields will be infered and they'll be made
        available in the app for querying and metrics.

        Args:
            key (str): The key for your metadata field
            val (Union[str, int, float, bool]): value
            val_type (Literal["str", "int", "float", "bool"], optional): type of val as string. Defaults to None.
        """
        assert_valid_name(key)
        # Validates that neither val or type is None
        if val is None and val_type is None:
            raise Exception(
                f"For frame_id {self.frame_id}: User Metadata key {key} must provide "
                f"scalar value or expected type of scalar value if None"
            )
        # Validates that val has an accepted type
        if val is not None and type(val) not in TYPE_PRIMITIVE_TO_STRING_MAP:
            raise Exception(
                f"For frame_id {self.frame_id}: User Metadata Value {val} "
                f"not in accepted scalar value types {TYPE_PRIMITIVE_TO_STRING_MAP.values()}"
            )
        # Validates that val_type has an accepted type
        if val_type and val_type not in TYPE_PRIMITIVE_TO_STRING_MAP.values():
            raise Exception(
                f"For frame_id {self.frame_id}: User Metadata Value Type {val_type} "
                f"not in accepted scalar value types {TYPE_PRIMITIVE_TO_STRING_MAP.values()}"
            )

        # Sets val_type if it is not set
        if val_type is None:
            val_type = TYPE_PRIMITIVE_TO_STRING_MAP[type(val)]

        # Checks that inferred type matches what the user put in val_type
        if val is not None:
            for (
                primitive,
                type_string,
            ) in TYPE_PRIMITIVE_TO_STRING_MAP.items():
                if type(val) is primitive and val_type != type_string:
                    raise Exception(
                        f"For frame_id {self.frame_id}, metadata key: {key}, value: {val}, "
                        f"type is inferred as {type_string} but provided type was {val_type}"
                    )

        self.user_metadata.append((key, val, val_type, "scalar"))

    def add_user_metadata_list(
        self,
        key: str,
        val: USER_METADATA_SEQUENCE,
        list_elt_type: Optional[USER_METADATA_PRIMITIVE_TYPES] = None,
    ) -> None:
        """Add a user provided metadata list field.

        The types of these metadata fields will be infered and they'll be made
        available in the app for querying and metrics.

        Args:
            key (str): The key for your metadata field
            val (Union[List[int], List[str], List[bool], List[float], Tuple[int], Tuple[str], Tuple[bool], Tuple[float]]): value
            list_elt_type (Literal["str", "int", "float", "bool"], optional): type of list elements as string. Applies to all members of val. Defaults to None.
        """
        assert_valid_name(key)
        # Validates that neither val or type or mode is None
        if val is None and list_elt_type is None:
            raise Exception(
                f"For frame_id {self.frame_id}: User Metadata list key {key} must provide "
                f"list or expected type of list elements if None"
            )

        # Validates that val has an accepted type
        if val is not None:
            if type(val) not in (list, tuple):
                raise Exception(
                    f"For frame_id {self.frame_id}: User Metadata list value {val} "
                    f"is not in accepted sequence types list, tuple."
                )
            if len(val) == 0 and not list_elt_type:
                raise Exception(
                    f"For frame_id {self.frame_id}: User Metadata list value {val} "
                    f"is an empty {type(val).__name__}. "
                    "Please specify the expected scalar value type for its elements by passing a list_elt_type"
                )

            # validate that all elements in the list are the same primitive type, based on the first element
            if len(val) > 0:
                found_val_types = {type(el) for el in val}

                if len(found_val_types) > 1:
                    raise Exception(
                        f"For frame_id {self.frame_id}: User Metadata list value {val} "
                        f"has elements of invalid type. Expected all elements to be of the same type, found types of {found_val_types}"
                    )

                inferred_val_type = found_val_types.pop()
                if inferred_val_type not in TYPE_PRIMITIVE_TO_STRING_MAP:
                    raise Exception(
                        f"For frame_id {self.frame_id}: User Metadata list value {val} contains elements "
                        f"not in accepted scalar value types {TYPE_PRIMITIVE_TO_STRING_MAP.values()}"
                    )

        # Validates that list_elt_type has an accepted type
        if list_elt_type and list_elt_type not in TYPE_PRIMITIVE_TO_STRING_MAP.values():
            raise Exception(
                f"For frame_id {self.frame_id}: User Metadata list element type {list_elt_type} "
                f"not in accepted scalar value types {TYPE_PRIMITIVE_TO_STRING_MAP.values()}"
            )

        # Checks that inferred type matches what the user put in list_elt_type
        if list_elt_type is not None and val is not None and len(val) > 0:
            inferred_val_type = type(val[0])
            for (
                primitive,
                type_string,
            ) in TYPE_PRIMITIVE_TO_STRING_MAP.items():
                if inferred_val_type is primitive and list_elt_type != type_string:
                    raise Exception(
                        f"For frame_id {self.frame_id}, metadata key: {key}, value: {val}, "
                        f"element type is inferred as {type_string} but provided type was {list_elt_type}"
                    )

        # Sets list_elt_type if it is not set
        if list_elt_type is None:
            inferred_val_type = type(val[0])
            list_elt_type = TYPE_PRIMITIVE_TO_STRING_MAP[inferred_val_type]

        self.user_metadata.append((key, val, list_elt_type, "list"))

    def add_geo_latlong_data(self, lat: float, lon: float) -> None:
        """Add a user provided EPSG:4326 WGS84 lat long pair to each frame

        We expect these values to be floats

        Args:
            lat (float): lattitude of Geo Location
            lon (float): longitude of Geo Location
        """
        if not (isinstance(lat, float) and isinstance(lon, float)):
            raise Exception(
                f"Lattitude ({lat}) and Longitude ({lon}) must both be floats."
            )

        self.geo_data["geo_EPSG4326_lat"] = lat
        self.geo_data["geo_EPSG4326_lon"] = lon

    def add_point_cloud_pcd(
        self,
        *,
        sensor_id: str,
        pcd_url: str,
        coord_frame_id: Optional[str] = None,
        date_captured: Optional[str] = None,
    ) -> None:
        """Add a point cloud sensor data point to this frame,
        contained in PCD format. ascii, binary, and binary_compressed formats are supported.
        Numeric values for the following column names are expected:
        x, y, z, intensity (optional), range (optional)

        Args:
            sensor_id (str): sensor id
            pcd_url (str): URL to PCD formated data
            coord_frame_id (Optional[str], optional): The coordinate frame id. Defaults to None.
            date_captured (Optional[str], optional): ISO formatted date. Defaults to None.
        """
        if not isinstance(sensor_id, str):
            raise Exception("sensor ids must be strings")

        if date_captured is None:
            date_captured = str(datetime.datetime.now())

        if coord_frame_id is None:
            coord_frame_id = "world"

        data_urls = {
            "pcd_url": pcd_url,
        }

        if not self._coord_frame_exists(coord_frame_id):
            if coord_frame_id == "world":
                self._add_coordinate_frame(
                    {
                        "coordinate_frame_id": coord_frame_id,
                        "coordinate_frame_type": "WORLD",
                    }
                )
            else:
                raise Exception(
                    "Coordinate frame {} does not exist.".format(coord_frame_id)
                )

        self.sensor_data.append(
            {
                "coordinate_frame": coord_frame_id,
                "data_urls": data_urls,
                "date_captured": date_captured,
                "sensor_id": sensor_id,
                "sensor_metadata": {},
                "sensor_type": "POINTCLOUD_PCD_V0",
            }
        )

    def add_point_cloud_bins(
        self,
        *,
        sensor_id: str,
        pointcloud_url: str = None,
        kitti_format_url: str = None,
        intensity_url: str = None,
        range_url: str = None,
        coord_frame_id: Optional[str] = None,
        date_captured: Optional[str] = None,
    ) -> None:
        """Add a point cloud sensor data point to this frame, contained in dense binary files of
        little-endian values, similar to the raw format of KITTI lidar data. You can provide
        a combination of the following values, as long as at least either kitti_format_url or
        pointcloud_url are provided.

        Args:
            sensor_id (str): Sensor id
            pointcloud_url (Optional[str]): URL for the pointcloud: float32 [x1, y1, z1, x2, y2, z2, ...]
            kitti_format_url (Optional[str]): URL for the pointcloud + intensity: float32 [x1, y1, z1, i1, x2, y2, z2, i2, ...]
            intensity_url (Optional[str]): URL for the Intensity Pointcloud: unsigned int32 [i1, i2, ...]
            range_url (Optional[str]): URL for the Range Pointcloud: float32 [r1, r2, ...]
            coord_frame_id (Optional[str], optional): Id for the Coordinate Frame. Defaults to None.
            date_captured (Optional[str], optional): ISO formatted date. Defaults to None.
        """
        if not isinstance(sensor_id, str):
            raise Exception("sensor ids must be strings")

        if pointcloud_url is None and kitti_format_url is None:
            raise Exception(
                "Either pointcloud_url or kitti_format_url must be provided."
            )

        if pointcloud_url is not None and kitti_format_url is not None:
            raise Exception(
                "Only one of pointcloud_url or kitti_format_url must be provided."
            )

        if date_captured is None:
            date_captured = str(datetime.datetime.now())

        if coord_frame_id is None:
            coord_frame_id = "world"

        data_urls = {}
        if pointcloud_url is not None:
            data_urls["pointcloud_url"] = pointcloud_url
        if kitti_format_url is not None:
            data_urls["kitti_format_url"] = kitti_format_url
        if range_url is not None:
            data_urls["range_url"] = range_url
        if intensity_url is not None:
            data_urls["intensity_url"] = intensity_url

        if not self._coord_frame_exists(coord_frame_id):
            if coord_frame_id == "world":
                self._add_coordinate_frame(
                    {
                        "coordinate_frame_id": coord_frame_id,
                        "coordinate_frame_type": "WORLD",
                    }
                )
            else:
                raise Exception(
                    "Coordinate frame {} does not exist.".format(coord_frame_id)
                )

        self.sensor_data.append(
            {
                "coordinate_frame": coord_frame_id,
                "data_urls": data_urls,
                "date_captured": date_captured,
                "sensor_id": sensor_id,
                "sensor_metadata": {},
                "sensor_type": "POINTCLOUD_V0",
            }
        )

    def add_obj(
        self,
        *,
        sensor_id: str,
        obj_url: str,
        coord_frame_id: Optional[str] = None,
        date_captured: Optional[str] = None,
    ) -> None:
        """Add a .obj file to the frame for text based geometry

        Args:
            sensor_id (str): sensor id
            obj_url (str): URL to where the object is located
            coord_frame_id (Optional[str], optional): ID for the coordinate frame. Defaults to None.
            date_captured (Optional[str], optional): ISO formatted date. Defaults to None.
        """
        if not isinstance(sensor_id, str):
            raise Exception("sensor ids must be strings")

        if date_captured is None:
            date_captured = str(datetime.datetime.now())

        if coord_frame_id is None:
            coord_frame_id = "world"

        data_urls = {
            "obj_url": obj_url,
        }

        if not self._coord_frame_exists(coord_frame_id):
            self._add_coordinate_frame(
                {
                    "coordinate_frame_id": coord_frame_id,
                    "coordinate_frame_type": "WORLD",
                }
            )

        self.sensor_data.append(
            {
                "coordinate_frame": coord_frame_id,
                "data_urls": data_urls,
                "date_captured": date_captured,
                "sensor_id": sensor_id,
                "sensor_metadata": {},
                "sensor_type": "OBJ_V0",
            }
        )

    def add_image(
        self,
        *,
        sensor_id: str,
        image_url: str,
        preview_url: Optional[str] = None,
        date_captured: Optional[str] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
    ) -> None:
        """Add an image "sensor" data to this frame.

        Args:
            sensor_id (str): The id of this sensor.
            image_url (str): The URL to load this image data.
            preview_url (Optional[str], optional): A URL to a compressed version of the image. It must be the same pixel dimensions as the original image. Defaults to None.
            date_captured (Optional[str], optional): ISO formatted date. Defaults to None.
            width (Optional[int], optional): The width of the image in pixels. Defaults to None.
            height (Optional[int], optional): The height of the image in pixels. Defaults to None.
        """
        if not isinstance(sensor_id, str):
            raise Exception("sensor ids must be strings")

        sensor_metadata = {}
        if width is not None:
            if not isinstance(width, int):
                raise Exception("width must be an int")
            sensor_metadata["width"] = width

        if height is not None:
            if not isinstance(height, int):
                raise Exception("height must be an int")
            sensor_metadata["height"] = height

        if date_captured is None:
            date_captured = str(datetime.datetime.now())

        data_urls = {"image_url": image_url}
        if preview_url is not None:
            data_urls["preview_url"] = preview_url

        self._add_coordinate_frame(
            {"coordinate_frame_id": sensor_id, "coordinate_frame_type": "IMAGE"}
        )
        self.sensor_data.append(
            {
                "coordinate_frame": sensor_id,
                "data_urls": data_urls,
                "date_captured": date_captured,
                "sensor_id": sensor_id,
                "sensor_metadata": sensor_metadata,
                "sensor_type": "IMAGE_V0",
            }
        )

    def add_image_overlay(
        self,
        *,
        sensor_id: str,
        overlay_id: str,
        image_url: str,
        date_captured: Optional[str] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
    ) -> None:
        """Add an image overlay for the given "sensor" to this frame.

        Args:
            sensor_id (str): The id of this sensor.
            overlay_id (str): The id of this overlay.
            image_url (str): The URL to load this image data.
            date_captured (Optional[str], optional): ISO formatted date. Defaults to None.
            width (Optional[int], optional): The width of the image in pixels. Defaults to None.
            height (Optional[int], optional): The height of the image in pixels. Defaults to None.
        """
        if not isinstance(sensor_id, str):
            raise Exception("sensor ids must be strings")

        if not isinstance(overlay_id, str):
            raise Exception("overlay ids must be strings")

        sensor_metadata: dict[str, Union[str, int]] = {"overlay_id": overlay_id}
        if width is not None:
            if not isinstance(width, int):
                raise Exception("width must be an int")
            sensor_metadata["width"] = width

        if height is not None:
            if not isinstance(height, int):
                raise Exception("height must be an int")
            sensor_metadata["height"] = height

        if date_captured is None:
            date_captured = str(datetime.datetime.now())

        data_urls = {"image_url": image_url}

        self._add_coordinate_frame(
            {"coordinate_frame_id": sensor_id, "coordinate_frame_type": "IMAGE"}
        )
        self.sensor_data.append(
            {
                "coordinate_frame": sensor_id,
                "data_urls": data_urls,
                "date_captured": date_captured,
                "sensor_id": sensor_id,
                "sensor_metadata": sensor_metadata,
                "sensor_type": "IMAGE_OVERLAY_V0",
            }
        )

    def add_audio(
        self,
        *,
        sensor_id: str,
        audio_url: str,
        date_captured: Optional[str] = None,
    ) -> None:
        """Add an audio "sensor" data to this frame.

        Args:
            sensor_id (str): The id of this sensor.
            audio_url (str): The URL to load this audio data (mp3, etc.).
            date_captured (str, optional): ISO formatted date. Defaults to None.
        """
        if not isinstance(sensor_id, str):
            raise Exception("sensor ids must be strings")

        sensor_metadata: Dict[str, Any] = {}
        if date_captured is None:
            date_captured = str(datetime.datetime.now())

        data_urls = {"audio_url": audio_url}

        self._add_coordinate_frame(
            {"coordinate_frame_id": sensor_id, "coordinate_frame_type": "AUDIO"}
        )
        self.sensor_data.append(
            {
                "coordinate_frame": sensor_id,
                "data_urls": data_urls,
                "date_captured": date_captured,
                "sensor_id": sensor_id,
                "sensor_metadata": sensor_metadata,
                "sensor_type": "AUDIO_V0",
            }
        )

    def add_video(
        self,
        *,
        sensor_id: str,
        video_url: str,
        date_captured: Optional[str] = None,
    ) -> None:
        """Add a video "sensor" data to this frame.

        Args:
            sensor_id (str): The id of this sensor.
            video_url (str): The URL to load this video data (mp4, webm, etc.).
            date_captured (str, optional): ISO formatted date. Defaults to None.
        """
        if not isinstance(sensor_id, str):
            raise Exception("sensor ids must be strings")

        sensor_metadata: Dict[str, Any] = {}
        if date_captured is None:
            date_captured = str(datetime.datetime.now())

        data_urls = {"video_url": video_url}

        self._add_coordinate_frame(
            {"coordinate_frame_id": sensor_id, "coordinate_frame_type": "VIDEO"}
        )
        self.sensor_data.append(
            {
                "coordinate_frame": sensor_id,
                "data_urls": data_urls,
                "date_captured": date_captured,
                "sensor_id": sensor_id,
                "sensor_metadata": sensor_metadata,
                "sensor_type": "VIDEO_V0",
            }
        )

    def add_coordinate_frame_3d(
        self,
        *,
        coord_frame_id: str,
        position: Optional[Dict[POSITION_KEYS, Union[int, float]]] = None,
        orientation: Optional[Dict[ORIENTATION_KEYS, Union[int, float]]] = None,
        parent_frame_id: Optional[str] = None,
    ) -> None:
        """Add a 3D Coordinate Frame.

        Args:
            coord_frame_id (str): String identifier for this coordinate frame
            position (Optional[Dict[POSITION, Union[int, float]]], optional): Dict of the form {x, y, z}. Defaults to None.
            orientation (Optional[Dict[ORIENTATION, Union[int, float]]], optional): Quaternion rotation dict of the form {w, x, y, z}. Defaults to None.
            parent_frame_id (Optional[str], optional): String id of the parent coordinate frame. Defaults to None.
        """

        if not isinstance(coord_frame_id, str):
            raise Exception("coord_frame_id must be a string")

        if coord_frame_id == "world":
            raise Exception("coord_frame_id cannot be world")

        if self._coord_frame_exists(coord_frame_id):
            raise Exception("Coordinate frame already exists.")

        # If world doesn't exist, make the world coordinate frame
        if not self._coord_frame_exists("world"):
            self._add_coordinate_frame(
                {
                    "coordinate_frame_id": "world",
                    "coordinate_frame_type": "WORLD",
                }
            )

        if position is None:
            position = {"x": 0, "y": 0, "z": 0}

        if orientation is None:
            orientation = {"w": 1, "x": 0, "y": 0, "z": 0}

        if parent_frame_id is None:
            parent_frame_id = "world"

        metadata = {
            "position": position,
            "orientation": orientation,
            "parent_frame_id": parent_frame_id,
        }

        self._add_coordinate_frame(
            {
                "coordinate_frame_id": coord_frame_id,
                "coordinate_frame_type": "WORLD",
                "coordinate_frame_metadata": json.dumps(metadata),
            }
        )

    def add_text(
        self, *, sensor_id: str, text: str, date_captured: Optional[str] = None
    ) -> None:
        """Add a text "sensor" data to this frame.

        Args:
            sensor_id (str): The id of this sensor.
            text (str): The text body.
            date_captured (str, optional): ISO formatted date. Defaults to None.
        """

        if not isinstance(sensor_id, str):
            raise Exception("sensor ids must be strings")

        if date_captured is None:
            date_captured = str(datetime.datetime.now())

        data_urls = {"text": text}
        self._add_coordinate_frame(
            {"coordinate_frame_id": sensor_id, "coordinate_frame_type": "TEXT"}
        )
        self.sensor_data.append(
            {
                "coordinate_frame": sensor_id,
                "data_urls": data_urls,
                "date_captured": date_captured,
                "sensor_id": sensor_id,
                "sensor_metadata": {},
                "sensor_type": "TEXT",
            }
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert this frame into a dictionary representation.

        Returns:
            dict: dictified frame
        """
        row = {
            "task_id": self.frame_id,
            "date_captured": self.date_captured,
            "device_id": self.device_id,
            "coordinate_frames": self.coordinate_frames,
            "sensor_data": self.sensor_data,
            "geo_data": self.geo_data,
        }
        user_metadata_types = {}
        user_metadata_modes = {}

        for k, v, vt, vm in self.user_metadata:
            namespaced = k
            if "user__" not in namespaced:
                namespaced = "user__" + namespaced
            # cast to BQ-serializable list if tuple
            row[namespaced] = list(v) if isinstance(v, tuple) else v
            user_metadata_types[namespaced] = vt
            user_metadata_modes[namespaced] = vm

        row["user_metadata_types"] = user_metadata_types
        row["user_metadata_modes"] = user_metadata_modes
        return row


class UpdateFrame(BaseFrame):
    is_snapshot: bool

    def __init__(
        self,
        *,
        frame_id: str,
        update_type: UpdateType,
        is_snapshot: bool = True,
        date_captured: Optional[str] = None,
        device_id: Optional[str] = None,
    ):
        super().__init__(
            frame_id=frame_id, date_captured=date_captured, device_id=device_id
        )
        self.is_snapshot = is_snapshot

    def to_dict(self) -> Dict[str, Any]:
        """Convert this frame into a dictionary representation.

        Returns:
            dict: dictified frame
        """

        if self.is_snapshot:
            return super().to_dict()
        else:
            raise Exception("Not Implemented")
