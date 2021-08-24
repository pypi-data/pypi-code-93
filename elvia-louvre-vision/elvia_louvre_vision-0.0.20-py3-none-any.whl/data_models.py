from azure.cognitiveservices.vision.customvision.training.models import ImageFileCreateEntry, ImageUrlCreateEntry, Iteration, Region, Tag
from dataclasses import dataclass, field
from elvia_louvre.data_models import ImageData
from elvia_louvre.errors import LouvreValueError
from elvia_louvre.louvre_client import LouvreClient
import json
import math
from typing import Any, Dict, List, Optional, Set, Tuple, Union
import uuid

from louvre_vision.config import Config
from louvre_vision.images import ImageMethods
from louvre_vision.methods import Methods


@dataclass
class TrainingImage:

    identifier: str

    def __lt__(self, other):
        """Lower-than operator, used when sorting lists of instances of this class."""
        return self.identifier < other.identifier

    def __hash__(self):
        return hash(self.identifier)

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    @staticmethod
    def get_tag_id(label: str, tags: List[Tag]) -> str:
        """
        Given an image label or region tag, return the corresponding tag id.
        
        :param str label: Name of the label or category for which the tag id is desired.
        :param list tags: List of Tag objects, coming from the Custom Vision SDK, that represent existing tags in a Custom Vision project.
        :rtype: str
        :raises LouvreValueError:
        """

        tag_id = next((tag.id for tag in tags if tag.name == label), None)
        if tag_id is None:
            raise LouvreValueError(f'No tag.id found for tag name: {label}')

        return tag_id

    def get_imagecreateentry(
        self,
        tags: List[Tag],
        louvre_client: LouvreClient,
        using_production_images: bool = True
    ) -> Union[ImageUrlCreateEntry, ImageFileCreateEntry, None]:
        """
        This method is meant to be abstract and overridden in subclasses.

        :param list tags: List of Tag objects representing existing tags in a Custom Vision project.
        :param LouvreClient louvre_client: A LouvreClient instance with access to where the current image exists.
        :param bool using_production_images: Whether to use production images. Defaults to True. Requires a LouvreClient instance access to production.
        :rtype: ImageUrlCreateEntry | ImageFileCreateEntry | None
        :raises NotImplementedError:
        """
        raise NotImplementedError()

    @staticmethod
    def _create_imagecreateentry_from_url(
        image_url: str,
        tag_ids: List[str] = [],
        regions: List[Region] = []
    ) -> Union[ImageUrlCreateEntry, ImageFileCreateEntry]:

        file_size = Methods.get_remote_file_size(file_url=image_url)

        return ImageUrlCreateEntry(
            url=image_url, tag_ids=tag_ids, regions=regions
        ) if file_size and file_size < Config.custom_vision_max_training_file_size else ImageFileCreateEntry(
            name=Methods.extract_filename(file_path=image_url),
            contents=ImageMethods.resize_from_url(
                image_url=image_url,
                image_longer_side=Config.image_longer_side),
            tag_ids=tag_ids,
            regions=regions)

    @staticmethod
    def _create_imagecreateentry_from_image_data(
        image_data: ImageData,
        tag_ids: List[str] = [],
        regions: List[Region] = [],
    ) -> Union[ImageUrlCreateEntry, ImageFileCreateEntry, None]:

        image_entry = ImageMethods.get_image_from_image_data(
            image_data=image_data,
            max_file_size=Config.custom_vision_max_training_file_size)

        if image_entry.is_empty:
            return None

        # image_payload is either a sasuri string or bytes
        if image_entry.sasuri:
            return ImageUrlCreateEntry(url=image_entry.sasuri,
                                       tag_ids=tag_ids,
                                       regions=regions)
        # image_payload is bytes
        image_variant = image_data.get_variant(
            ImageMethods.select_preferred_image_variant_for_custom_vision(
                image_data=image_data))
        file_name = Methods.extract_filename(
            file_path=image_variant.sasuri
        ) if image_variant else image_data.image_id
        return ImageFileCreateEntry(name=file_name,
                                    contents=image_entry.file_bytes,
                                    tag_ids=tag_ids,
                                    regions=regions)


@dataclass
class ClassificationTrainingImage(TrainingImage):
    """
    Represent an object detection training image.

    :param list labels: List of categories the current training image belongs to.
    """

    labels: List[str]

    def __hash__(self):
        return hash(self.identifier + str((label for label in self.labels)))

    def get_imagecreateentry(
        self,
        tags: List[Tag],
        louvre_client: LouvreClient,
        using_production_images: bool = True
    ) -> Union[ImageUrlCreateEntry, ImageFileCreateEntry, None]:
        """
        Returns an instance of either ``ImageUrlCreateEntry`` or ``ImageFileCreateEntry`` representing the current training image.
        The result can be sent to Custom Vision.

        :param list tags: List of Tag objects representing tags available in a Custom Vision project. 
        :param LouvreClient louvre_client: LouvreClient instance with access to the Louvre environment where this image exists.
        :param bool using_production_images: Whether to use production credentials. Defaults to True. True requires a LouvreClient instance with access to production.
        :rtype: ImageUrlCreateEntry | ImageFileCreateEntry | None
        :raises LouvreImageNotFound:
        :raises LouvreKeyError:
        :raises LouvreQueryError:
        :raises RequestException:
        """
        image_tag_ids = []
        for label in list(set(self.labels)):
            image_tag_ids.append(super().get_tag_id(label=label, tags=tags))
        if Methods.is_string_url(self.identifier):
            return super()._create_imagecreateentry_from_url(
                image_url=self.identifier, tag_ids=image_tag_ids)
        image_data = louvre_client.get_image_data(
            image_id=self.identifier,
            using_production_images=using_production_images)
        return super()._create_imagecreateentry_from_image_data(
            image_data=image_data, tag_ids=image_tag_ids)


@dataclass
class BoundingBoxParams:
    """
    :var str TOP:
    :var str LEFT:
    :var str WIDTH:
    :var str HEIGHT:
    """
    TOP = 'top'
    LEFT = 'left'
    WIDTH = 'width'
    HEIGHT = 'height'


@dataclass
class RegionBoundingBox:

    top: float
    left: float
    width: float
    height: float
    decimal_places: int = Config.predictions_rounding_decimal_places

    def __str__(self) -> str:
        strings = [
            f'{BoundingBoxParams.TOP} = {str(round(self.top, self.decimal_places))}; ',
            f'{BoundingBoxParams.LEFT} = {str(round(self.left, self.decimal_places))}; ',
            f'{BoundingBoxParams.WIDTH} = {str(round(self.width, self.decimal_places))}; ',
            f'{BoundingBoxParams.HEIGHT} = {str(round(self.height, self.decimal_places))}'
        ]
        return ''.join(strings)

    def __repr__(self) -> str:
        return self.__str__()

    def to_tuple(self, height: int,
                 width: int) -> Tuple[float, float, float, float]:
        """Return as tuple: (left, upper, right, lower)"""
        left = round(self.left * width, self.decimal_places)
        upper = round(self.top * height, self.decimal_places)
        right = round(left + width * self.width, self.decimal_places)
        lower = round(upper + height * self.height, self.decimal_places)

        return (left, upper, right, lower)

    def to_dict(self) -> Dict[str, str]:
        """
        Return as a dict with serialised values, so that MetadataUpdater can accept it.
        
        :var str top:
        :var str left:
        :var str width:
        :var str height:
        :var int decimal_places:
        :rtype: Dict[str, str]
        """
        return {
            BoundingBoxParams.TOP: str(round(self.top, self.decimal_places)),
            BoundingBoxParams.LEFT: str(round(self.left, self.decimal_places)),
            BoundingBoxParams.WIDTH: str(round(self.width,
                                               self.decimal_places)),
            BoundingBoxParams.HEIGHT:
            str(round(self.height, self.decimal_places))
        }


@dataclass
class ImageRegion:

    bounding_box: RegionBoundingBox
    tag_name: str

    def to_dict(self) -> dict:
        return {
            'tag_name': self.tag_name,
            'top': self.bounding_box.top,
            'left': self.bounding_box.left,
            'width': self.bounding_box.width,
            'height': self.bounding_box.height
        }


@dataclass
class ObjectDetectionTrainingImage(TrainingImage):
    """
    Represent an object detection training image.

    :param list regions: List of ``ImageRegion`` objects representing the regions present on the current training image.
    """

    regions: List[ImageRegion]

    def __hash__(self):
        return hash(self.identifier + str(self.regions))

    @property
    def unique_tags(self) -> Set[str]:
        """
        Return the unique tag names present in the image.
        
        :rtype: set
        """
        return set([region.tag_name for region in self.regions])

    def get_imagecreateentry(
        self,
        tags: List[Tag],
        louvre_client: LouvreClient,
        using_production_images: bool = True
    ) -> Union[ImageUrlCreateEntry, ImageFileCreateEntry, None]:
        """
        Returns an instance of either ``ImageUrlCreateEntry`` or ``ImageFileCreateEntry`` representing the current training image.
        The result can be sent to Custom Vision.

        :param list tags: List of Tag objects representing tags available in a Custom Vision project. 
        :param LouvreClient louvre_client: LouvreClient instance with access to the Louvre environment where this image exists.
        :param bool using_production_images: Whether to use production credentials. Defaults to True. True requires a LouvreClient instance with access to production.
        :rtype: ImageUrlCreateEntry | ImageFileCreateEntry | None
        :raises LouvreImageNotFound:
        :raises LouvreKeyError:
        :raises LouvreQueryError:
        :raises RequestException:
        """
        regions = self._get_custom_vision_regions(tags=tags)
        if Methods.is_string_url(self.identifier):
            return super()._create_imagecreateentry_from_url(
                image_url=self.identifier, regions=regions)
        image_data = louvre_client.get_image_data(
            image_id=self.identifier,
            using_production_images=using_production_images)
        return super()._create_imagecreateentry_from_image_data(
            image_data=image_data, regions=regions)

    def _get_custom_vision_regions(self, tags: List[Tag]) -> List[Region]:
        """
        Return a list of Custom Vision Region objects representing the detected objects.
        The method output can be used in the creation of subsequent ImageXXXXCreateEntry objects.
        """
        regions: List[Region] = []
        for region in self.regions:
            regions.append(
                Region(tag_id=super().get_tag_id(label=region.tag_name,
                                                 tags=tags),
                       left=region.bounding_box.left,
                       top=region.bounding_box.top,
                       width=region.bounding_box.width,
                       height=region.bounding_box.height))

        return regions


@dataclass
class UploadImageEntry:
    """
    Represent a training image ready to be uploaded to a Custom Vision project.

    """

    image_create_entry: Union[ImageFileCreateEntry, ImageUrlCreateEntry]
    metadata: Dict[str, str]


@dataclass
class MetadataEntry:
    """
    Represent a single metadata entry under PACKAGE_NAME in the database.
    
    :param str image_id: Louvre image identifier
    :param str model_name: Machine learning model name
    :param api_version: Version number of this API
    :type api_version: str, optional
    :param execution_utctime: Execution UTC time
    :type execution_utctime: datetime, optional
    :param predictions: Prediction results
    :type predictions: List[Dict[str, str]], optional
    """
    image_id: str
    model_name: str
    api_version: Optional[str] = None
    iteration_publish_name: Optional[str] = None
    execution_utctime: Optional[str] = None
    predictions: Optional[List[Dict[str, str]]] = None

    def to_dict(self) -> Dict[str, Union[str, List[Dict[str, str]]]]:
        """
        Return a dict with serialised values. ``image_id`` is ignored.
        :rtype: dict
        """
        result: Dict[str, Union[str, List[Dict[str, str]]]] = {
            'model_name': self.model_name
        }
        if self.api_version:
            result['api_version'] = self.api_version
        if self.execution_utctime:
            result['execution_utctime'] = self.execution_utctime
        if self.predictions:
            result['predictions'] = self.predictions
        result['version'] = self.version

        return result

    def __hash__(self):
        return hash(self.image_id + self.model_name + str(self.api_version) +
                    str(self.iteration_publish_name))

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    @property
    def version(self) -> str:
        """
        Return an overall version value. Based on ``api_version`` and ``iteration_publish_name``.

        :rtype: str
        """
        return json.dumps({
            'api_version':
            str(self.api_version),
            'iteration_publish_name':
            str(self.iteration_publish_name)
        })


@dataclass
class AppProperties:
    """
    Encapsulates app properties used when updating image metadata.
    
    :param str app_name: Name of the app / api calling ImageEnhanceAPI
    :param str app_version: App version    
    :param str client_name: To be specified when performing metadata updates via ImageEnhanceAPI 
    :param list allowed_model_names: List of all allowed model names under the metadata tag ``app_name``. Used when updating the image metadata.
    """
    app_name: str
    app_version: str
    client_name: str
    allowed_model_names: List[str]


@dataclass
class ResultBundle:
    """
    Encapsulates prediction results to be passed on to MetadataUpdater.

    :param str model_name:
    :param list predictions:
    :param iteration_publish_name: 
    :type iteration_publish_name: str, optional
    :param dict other_metadata:     
    """

    model_name: str
    predictions: List[Dict[str, str]]
    iteration_publish_name: Optional[str] = None
    other_metadata: Dict[str, Any] = field(default_factory=dict)


# Incoming requests:
# Log-friendly classes that encapsulate the information of incoming HTTP requests:


@dataclass
class Request:
    """
    Represent an incoming request.

    :param str endpoint: Endpoint name
    :param str model_name: Model name
    :param str image_identifier: Image identifier 
    """
    endpoint: str
    model_name: str
    image_identifier: str

    def __post_init__(self):
        """Generate a unique request ID to make easier the tracking of a particular request."""
        self.request_id = str(uuid.uuid4())

    def __str__(self) -> str:
        raise NotImplementedError()


@dataclass
class EndpointRequest(Request):
    """
    Represent an incoming request.

    :param str endpoint: Endpoint name
    :param str model_name: Model name
    :param str image_identifier: Image identifier 
    :param bool using_production_images: Whether to use production images
    :param float probability_threshold: Cutoff probability value between 0 and 1
    """
    using_production_images: bool
    probability_threshold: float

    def __str__(self) -> str:
        return \
f'''
{self.__class__.__name__}:
request_id= {str(self.request_id)};
endpoint= {str(self.endpoint)};
ImageId= {str(self.image_identifier)};
model_name= {str(self.model_name)};
using_production_images= {str(self.using_production_images)};
probability_threshold= {str(self.probability_threshold)};
'''


@dataclass
class PluginEndpointRequest(Request):
    """
    Represent an incoming request triggered by PluginTrigger.

    :param str endpoint: Endpoint name
    :param str model_name: Model name
    :param str image_identifier: Image identifier 
    :param str plugin_id: Plugin identifier
    """
    plugin_id: str

    def __str__(self) -> str:
        return \
f'''
{self.__class__.__name__}:
request_id= {str(self.request_id)};
endpoint= {str(self.endpoint)};
ImageId= {str(self.image_identifier)};
model_name= {str(self.model_name)};
PluginId= {str(self.plugin_id)};
'''


# Data strutures representing the incoming prediction requests, after having checked
# that the required parameters were correctly specified, the models exist etc.:


@dataclass
class PredictionRequest:

    endpoint_request: EndpointRequest


@dataclass
class PluginPredictionRequest:

    endpoint_request: PluginEndpointRequest


@dataclass
class CustomVisionPredictionRequest(PredictionRequest):

    model: Iteration


@dataclass
class CustomVisionPluginPredictionRequest(PluginPredictionRequest):

    model: Iteration


# Prediction results:


@dataclass
class PredictionResult:
    probability: float

    def to_dict(self) -> Dict[str, str]:
        raise NotImplementedError()


@dataclass
class ClassificationPredictionResult(PredictionResult):
    tag_name: str

    def to_dict(self) -> Dict[str, str]:
        return {
            'probability':
            str(
                round(self.probability,
                      Config.predictions_rounding_decimal_places)),
            'tag_name':
            self.tag_name
        }


@dataclass
class ObjectDetectionPredictionResult(PredictionResult):
    region: ImageRegion

    def to_dict(self) -> Dict[str, str]:

        result = {'bounding box': str(self.region.bounding_box)}
        if self.probability and not math.isnan(self.probability):
            result['probability'] = str(
                round(self.probability,
                      Config.predictions_rounding_decimal_places))
        if self.region.tag_name:
            result['tag_name'] = self.region.tag_name
        return result
