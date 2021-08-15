#  Copyright (c) 2020 Caliber Data Labs.
#  All rights reserved.
#

from datetime import datetime

import pytz

TIMESTAMP_FIELD = "timestamp"  # todo remove the same variable from tools/constant
AUXILIARY_KEY = "aux"
START_TIME_FIELD = "start_time"
END_TIME_FIELD = "end_time"
MAX_THREADS = 20


class JobConstants:
    STATUS_QUEUED = "queued"
    STATUS_RUNNING = "running"
    STATUS_FINISHED = "finished"
    STATUS_INITIALIZED = "initialized"
    STATUS_ABORTED = "aborted"
    STATUS_CANCELLED = "cancelled"


class OperationTypes:
    ANNOTATION = "annotation"
    SMOOTHING_TIME_SERIES = "smoothing_time_series"
    GROWTH_STAGES_EXTRACTION = "growth_stages_extraction"
    CDL_MASK_CREATION = "cdl_mask_creation"
    MULTISPECTRAL_TIME_SERIES_BUILDING = "multispectral_time_series_building"
    ROSBAGS_TO_XVIZ = "rosbags_to_xviz"
    DATASET_SIMILARITY_SEARCH = "dataset_similarity_search"
    CONSENSUS = "consensus"

    VALID_TYPES = {
        ANNOTATION,
        SMOOTHING_TIME_SERIES,
        GROWTH_STAGES_EXTRACTION,
        CDL_MASK_CREATION,
        MULTISPECTRAL_TIME_SERIES_BUILDING,
        ROSBAGS_TO_XVIZ,
        DATASET_SIMILARITY_SEARCH,
        CONSENSUS
    }


class JobTypes:
    EXTRACTION = "media_extraction"
    SET_ADDITION = "set_addition"
    SET_REMOVAL = "set_removal"
    ZIPPING = "zipping"
    SESSION_RESOLUTION = "session_resolution"
    SESSION_DELETION = "session_deletion"
    EVENT_DELETION = "event_deletion"
    ASSETS_REMOVAL = "media_removal"
    ENRICHMENT = "enrichment"
    IMAGE_COMPRESSION = 'image_compression'
    LIDAR_COMPRESSION = 'lidar_compression'
    VIDEO_COMPRESSION = 'video_compression'
    VIDEO_CONCATENATION = 'video_concatenation'
    SYNTHETIC_INDEXING = 'synthetic_indexing'
    COCO_FORMATTING = 'coco_formatting'
    VIDEO_EXTRACTION = 'video_extraction'
    IMAGE_EXTRACTION = 'image_extraction'
    LIDAR_EXTRACTION = 'lidar_extraction'
    GEO_EXTRACTION = 'geo_extraction'
    GENERIC_EXTRACTION = 'generic_extraction'
    SESSION_REGISTRATION = 'session_registration'
    VIDEO_INDEXING = 'video_indexing'
    ADD_EVENT_WITH_SEARCH = 'add_event_with_search'
    COORDINATE_INTERACTION = 'coordinate_interaction'
    ANNOTATIONS_COMPARISON = 'compare_annotations'
    SIMILARITY_BULK_INDEX = 'similarity_bulk_index'
    ANNOTATION_PROCESS = 'annotation_process'
    IMAGE_INFERENCE = "image_inference"
    UMAP_CREATION = "umap_creation"

    VALID_TYPES = {
        None,
        EXTRACTION,
        SET_ADDITION,
        SET_REMOVAL,
        ZIPPING,
        SESSION_RESOLUTION,
        ASSETS_REMOVAL,
        ENRICHMENT,
        IMAGE_COMPRESSION,
        LIDAR_COMPRESSION,
        VIDEO_COMPRESSION,
        VIDEO_CONCATENATION,
        SYNTHETIC_INDEXING,
        COCO_FORMATTING,
        VIDEO_EXTRACTION,
        IMAGE_EXTRACTION,
        LIDAR_EXTRACTION,
        GEO_EXTRACTION,
        GENERIC_EXTRACTION,
        SESSION_REGISTRATION,
        SESSION_DELETION,
        VIDEO_INDEXING,
        ADD_EVENT_WITH_SEARCH,
        EVENT_DELETION,
        COORDINATE_INTERACTION,
        ANNOTATIONS_COMPARISON,
        SIMILARITY_BULK_INDEX,
        ANNOTATION_PROCESS,
        UMAP_CREATION,
        IMAGE_INFERENCE
    } | OperationTypes.VALID_TYPES


class JobTags:
    USER_FACING = "user_facing"


class SessionTypes:
    ROSBAGS_SESSION_ID = "rosbags"
    VIDEOS_SESSION_ID = "videos"
    HLS_SESSION_ID = "hls"
    GENERIC_SESSION_ID = "generic"
    VALID_TYPES = {
        ROSBAGS_SESSION_ID,
        VIDEOS_SESSION_ID,
        HLS_SESSION_ID,
        GENERIC_SESSION_ID
    }


class AssetsConstants:
    # MODELS_ASSET_ID = "models"
    SESSIONS_ASSET_ID = "sessions"
    ANNOTATION_PROJECTS_ASSET_ID = "annotation_projects"
    ANNOTATIONS_ASSET_ID = "annotations"
    ANNOTATIONS_COMPARISONS_ASSET_ID = "annotations_comparisons"
    CONFIGS_ASSET_ID = "configs"
    IMAGES_ASSET_ID = "images"
    OBJECTS_ASSET_ID = "objects"
    LIDARS_ASSET_ID = "lidars"
    IMAGE_SEQUENCES_ASSET_ID = "image_sequences"
    VIDEOS_ASSET_ID = "videos"
    ROSBAGS_ASSET_ID = "rosbags"
    HLS_ASSET_ID = "geotifs"
    SETS_ASSET_ID = "sets"
    PROJECTS_ASSET_ID = "projects"
    OPERATIONS_ASSET_ID = "operations"
    JOBS_ASSET_ID = "jobs"
    ZIPFILES_ASSET_ID = "zipfiles"
    UDFS_ASSET_ID = "udfs"
    ZIPARRAYS_ASSET_ID = "ziparrays"
    SESSION_CONFIGURATIONS_ASSET_ID = "session_configurations"
    XVIZ_ASSET_ID = "xviz"
    LIDAR_SEQUENCES_ASSET_ID = "lidar_sequences"
    EMBEDDINGS_ASSET_ID = "embeddings"

    SESSIONS_MANAGER_ASSET_ID = "session_manager"  # TODO: This isn't really an asset
    # TENSORS_ASSET_ID = "tensors"  # TODO: Tensors aren't used

    VALID_ASSETS = {
        # MODELS_ASSET_ID,
        SESSIONS_ASSET_ID,
        ANNOTATION_PROJECTS_ASSET_ID,
        ANNOTATIONS_ASSET_ID,
        ANNOTATIONS_COMPARISONS_ASSET_ID,
        CONFIGS_ASSET_ID,
        IMAGES_ASSET_ID,
        OBJECTS_ASSET_ID,
        LIDARS_ASSET_ID,
        VIDEOS_ASSET_ID,
        ROSBAGS_ASSET_ID,
        HLS_ASSET_ID,
        SETS_ASSET_ID,
        PROJECTS_ASSET_ID,
        OPERATIONS_ASSET_ID,
        JOBS_ASSET_ID,
        ZIPFILES_ASSET_ID,
        ZIPARRAYS_ASSET_ID,
        SESSION_CONFIGURATIONS_ASSET_ID,
        XVIZ_ASSET_ID,
        SESSIONS_MANAGER_ASSET_ID,
        # TENSORS_ASSET_ID,
        IMAGE_SEQUENCES_ASSET_ID,
        LIDAR_SEQUENCES_ASSET_ID,
        EMBEDDINGS_ASSET_ID,
        UDFS_ASSET_ID
    }

    METADATA_ONLY_ASSETS = {
        SESSIONS_ASSET_ID,
        ANNOTATION_PROJECTS_ASSET_ID,
        # ANNOTATIONS_ASSET_ID,
        CONFIGS_ASSET_ID,
        SETS_ASSET_ID,
        PROJECTS_ASSET_ID,
        OPERATIONS_ASSET_ID,
        JOBS_ASSET_ID,
        SESSION_CONFIGURATIONS_ASSET_ID,
        XVIZ_ASSET_ID,
        SESSIONS_MANAGER_ASSET_ID,
        # TENSORS_ASSET_ID,
        LIDAR_SEQUENCES_ASSET_ID,
        ANNOTATIONS_COMPARISONS_ASSET_ID,
        OBJECTS_ASSET_ID,
    }


class SetsAssets:
    VALID_ASSET_TYPES = {
        AssetsConstants.IMAGES_ASSET_ID,
        AssetsConstants.OBJECTS_ASSET_ID,
        AssetsConstants.VIDEOS_ASSET_ID,
        AssetsConstants.ROSBAGS_ASSET_ID,
        AssetsConstants.SESSIONS_ASSET_ID,
        AssetsConstants.LIDARS_ASSET_ID,
        AssetsConstants.ANNOTATIONS_ASSET_ID,
        AssetsConstants.ZIPARRAYS_ASSET_ID,
        AssetsConstants.XVIZ_ASSET_ID,
    }


class SetsStates:
    READY = "ready"
    DELETE = "being deleted"
    MOVE = "moving assets"
    ZIP = "being zipped"
    POPULATING = "being populated"
    VALID_STATES = {
        READY,
        DELETE,
        MOVE,
        ZIP,
        POPULATING,
    }


class ConfigTypes:
    SEARCH = 'search'
    ANNOTATION_INSTRUCTION = 'annotation_instruction'
    ADMIN_PANEL = 'admin_panel'
    SESSION_VIEW = "session_view"
    SUMMARY_VIEW = "summary_view"
    HEADER_FILTER_GROUP = "header_filter_group"
    OBJECT_INTERACTION_RECIPE = "object_interaction_recipe"
    ANNOTATION_COMPARISON_CARD = "annotation_comparison_card"

    VALID_TYPES = {
        SEARCH,
        ANNOTATION_INSTRUCTION,
        ADMIN_PANEL,
        SESSION_VIEW,
        SUMMARY_VIEW,
        HEADER_FILTER_GROUP,
        OBJECT_INTERACTION_RECIPE,
        ANNOTATION_COMPARISON_CARD
    }


class EntityTypes:
    GEO_ENTITY_TYPE = 'geo'
    SCALAR_ENTITY_TYPE = 'scalar'
    VECTOR_ENTITY_TYPE = 'vector'
    STATE_ENTITY_TYPE = 'state'
    STATE_SET_ENTITY_TYPE = 'state_set'
    STATE_VECTOR_ENTITY_TYPE = 'state_vector'
    MEDIA = 'media'

    VALID_TYPES = {
        GEO_ENTITY_TYPE,
        SCALAR_ENTITY_TYPE,
        VECTOR_ENTITY_TYPE,
        STATE_VECTOR_ENTITY_TYPE,
        STATE_SET_ENTITY_TYPE,
        STATE_ENTITY_TYPE
    }


class EntityNames:
    """This is the name as it appears when searching."""
    WEATHER_CONDITIONS = "weather_conditions"
    OBJECTS = 'objects'
    IMAGE = 'image'
    VIDEO = 'video'
    LIDAR = 'lidar'
    ZIPARRAY = 'ziparray'
    GEOLOCATION = 'geolocation'
    COMMENT = 'comment'
    COMMENTATOR = 'commentator'
    NUMBER_OF_OBJECTS = 'number_of_objects'


CONSTRUCTED_EVENT_NAME = "constructed"
OBJECT_MASK_EVENT_NAME = "object_mask_interaction"
OBJECTS_EVENT_NAME = "objects_interaction"


class SummaryEntities:
    DEFAULT_ENTITIES_TO_SUMMARIZE = [
        "objects",
        "weather_descriptions",
        "country",
        "city",
        "comment",
        "commentator",
        CONSTRUCTED_EVENT_NAME]


class AssetEntities:
    """This is used as a blacklist in searchable fields."""
    IMAGE = 'image'
    VIDEO = 'video'
    LIDAR = 'lidar'
    ZIPARRAY = 'ziparray'
    GEOLOCATION_LAT = 'geolocation.lat'
    GEOLOCATION_LON = 'geolocation.lon'


class EntityInfluenceTypes:
    POINT = 'point'
    LINEAR_INTERPOLATION = 'linear_interpolation'
    LINEAR_INTERPOLATION_INTEGER = 'linear_interpolation_integer'
    GEO_INTERPOLATION = 'geo_interpolation'
    INTERVAL = 'interval'
    START_STOP = 'start_stop'
    AFFECT_FORWARD = 'affect_forward'
    AFFECT_BACKWARD = 'affect_backward'

    VALID_TYPES = {
        POINT,
        LINEAR_INTERPOLATION,
        LINEAR_INTERPOLATION_INTEGER,
        GEO_INTERPOLATION,
        INTERVAL,
        START_STOP,
        AFFECT_FORWARD,
        AFFECT_BACKWARD
    }


class AnnotationTypes:
    SEGMENTATION = "segmentation"
    TWO_D_BOUNDING_BOX = "two_d_bounding_box"
    CUBOID = "cuboid"
    POINT = "point"
    POLYGON = "polygon"
    LINE = "line"
    CLASSIFICATION = "classification"
    MIXED = "mixed"
    CUSTOM = "custom"

    VALID_TYPES = {
        SEGMENTATION,
        TWO_D_BOUNDING_BOX,
        CUBOID,
        POINT,
        POLYGON,
        LINE,
        CLASSIFICATION,
        CUSTOM,
        MIXED,
    }


class AnnotationMediaTypes:
    IMAGE = AssetsConstants.IMAGES_ASSET_ID
    VIDEO = AssetsConstants.VIDEOS_ASSET_ID
    LIDAR = AssetsConstants.LIDARS_ASSET_ID
    IMAGE_SEQUENCE = AssetsConstants.IMAGE_SEQUENCES_ASSET_ID
    LIDAR_SEQUENCE = AssetsConstants.LIDAR_SEQUENCES_ASSET_ID

    VALID_TYPES = {
        IMAGE,
        VIDEO,
        LIDAR,
        IMAGE_SEQUENCE,
        LIDAR_SEQUENCE,
    }


class AnnotationProviders:
    SCALE = "scale"
    SCALE_MOCKED = "scale_mocked"
    DEEPEN = "deepen"
    LABELBOX = "labelbox"
    COCO_ANNOTATOR = "coco_annotator"
    CVAT = "cvat"
    SUPERANNOTATE = "superannotate"

    VALID_PROVIDERS = {
        SCALE,
        SCALE_MOCKED,
        DEEPEN,
        LABELBOX,
        COCO_ANNOTATOR,
        CVAT,
        SUPERANNOTATE
    }


class SmoothingBands:
    RED = 'red'
    BLUE = 'blue'
    GREEN = 'green'
    NIR_NARROW = 'nir_narrow'
    SWIR1 = 'swir1'
    SWIR2 = 'swir2'
    NDVI = 'ndvi'

    VALID_BANDS = {
        RED,
        BLUE,
        GREEN,
        NIR_NARROW,
        SWIR1,
        SWIR2,
        NDVI,
    }


class SearchableFieldTypes:
    TIME = "time"
    TAG = "tag"
    TEXT = "text"
    NUMBER = "number"
    GEO = "geo"
    BOOLEAN = "boolean"


class Tagging:
    TIME = "time"
    TAG = "tag"
    TEXT = "text"
    NUMBER = "number"
    GEO = "geo"
    BOOLEAN = "boolean"


class TrafficObjectTagging:
    GOOGLE_VISION = 'google-vision'
    MRCNN = 'mrcnn'


class SetTags:
    AUTOMATED_SET_CREATION_TAG = 'automatically-generated'
    EXTRACTION_SET_TAG = 'extraction'
    ANNOTATION_SET_TAG = 'annotation'
    PRIMARY_SET_TAG = 'primary'


class WeatherStackAttributes:
    VISIBILITY = 'visibility'
    WEATHER_DESCRIPTION = 'weather_descriptions'


class RosbagsMessageTypes:
    IMAGE_MESSAGE_TYPE = "sensor_msgs/Image"
    FIX_MESSAGE_TYPE = "sensor_msgs/NavSatFix"
    IMU_MESSAGE_TYPE = "sensor_msgs/Imu"
    LIDAR_MESSAGE_TYPE = "sensor_msgs/PointCloud2"
    TF_MESSAGE_TYPE = "tf2_msgs/TFMessage"

    VALID_TYPES = {
        IMAGE_MESSAGE_TYPE,
        FIX_MESSAGE_TYPE,
        IMU_MESSAGE_TYPE,
        LIDAR_MESSAGE_TYPE,
        TF_MESSAGE_TYPE
    }


class Sensors:
    CAMERA = "camera"
    LIDAR = "lidar"
    RADAR = "radar"
    GPS = "gps"
    IMU = "imu"
    GENERIC = "generic"

    VALID_SENSORS = {
        CAMERA,
        LIDAR,
        RADAR,
        GPS,
        IMU,
        GENERIC
    }


class UsageOperationTypes:
    CREATE_VIDEO_SESSION = "create_video_session"
    CREATE_SET = "create_set"
    CREATE_PROJECT = "create_project"
    CREATE_ANNOTATION = "create_annotation"
    CREATE_ZIPFILE = "create_zipfile"
    CREATE_CONFIG = "create_config"
    CREATE_ENTITY = "create_entity"
    DO_VIDEO_EXTRACTION = "do_video_exaction"
    DO_IMAGE_EXTRACTION = "do_image_exaction"
    DO_LIDAR_EXTRACTION = "do_lidar_exaction"


class Time:
    START_OF_TIME_STRING = "1970-01-01T00:00:00Z"
    START_OF_TIME_DATETIME = datetime(1970, 1, 1, tzinfo=pytz.utc)
    END_OF_TIME_STRING = "2070-01-01T00:00:00Z"
    END_OF_TIME_DATETIME = datetime(2070, 1, 1, tzinfo=pytz.utc)


ACK_OK_RESPONSE = {"acknowledged": True}


class VideoTags:
    CONCATENATED = "concatenated"
    EXTRACTED = "extracted"
    RAW = "raw"


class AnnotationTags:
    EMPTY = "empty"
    CLEANED = "cleaned"


class AuxiliaryDataTypes:
    CONCATENATED_VIDEO = "concatenated_video"
    LIDAR_XVIZ = "lidar_xviz"


class EnrichmentTypes:
    CITY = "city"
    COUNTRY = "country"
    MRCNN_OBJECT_DETECTION = "mrcnn_object_detection"
    VISIBILITY = "visibility"
    WEATHER = "weather"


class AnnotationComparisonDefaultValues:
    LABEL_MAPPING = {
        'vehicle.car': 'car',
        'human.pedestrian.adult': 'person',
        'pedestrian': 'person',
        'vehicle.bus.rigid': 'bus',
        'vehicle.truck': 'truck',
        'human.pedestrian.construction_worker': 'person'
    }
    IGNORE_LABELS = ['background', 'blank']
    IOU_THRESHOLD = 0.0


class AnnotationComparisonConstants:
    COMPARISON_TASK_ID = "comparison_task_id"
    SHARED_META = [
        AUXILIARY_KEY, "sensor", "format"
    ]


class ImagePreProcessingOperations:
    NORMALIZE_THUMBNAIL_COLORS = "normalize_thumbnail_colors"
