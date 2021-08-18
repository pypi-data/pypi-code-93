from datetime import datetime
from elvia_louvre.data_models import UpdateMetadataRequest
from elvia_louvre.image_api import ImageData
from elvia_louvre.louvre_client import LouvreClient
import json
from json.decoder import JSONDecodeError
from typing import Any, Dict, List, Optional

from louvre_vision.data_models import MetadataEntry, AppProperties, ResultBundle


class MetadataUpdater():
    """
    Bridge between the prediction results and the metadata updater in elvia-louvre.
    """
    @staticmethod
    def update_metadata(result_bundle: ResultBundle, image_data: ImageData,
                        app_properties: AppProperties,
                        louvre_client: LouvreClient, plugin_id: str):
        """
        Update image metadata. 
        Existing predictions entries (stored under the PACKAGE_NAME field) will be overwritten, but only if model_name is the same. 
        Existing predictions entries that are not listed under 
        Existing other_metadata fields with the same key will be overwritten.

        :param ResultBundle result_bundle: Object containing model information and prediction results
        :param ImageData image_data: ImageData obtained from the Louvre client.
        :param AppProperties app_properties: Object encapsulating key app properties.
        :param LouvreClient louvre_client: LouvreClient instance with access to the Louvre environment where the image exists.
        :param str plugin_id: Plugin identifier, from the agent making the request

        :rtype: None

        :raises LouvreImageNotFound:
        :raises LouvreKeyError:
        :raises LouvreQueryError:                
        :raises RequestException:
        """

        # existing entries under the metadata key PACKAGE_NAME
        package_metadata = MetadataUpdater._get_package_metadata_entries_from_image_data(
            image_data=image_data, app_name=app_properties.app_name)

        # Exclude older entries with the same model_name or model_name values not in the "allowed list"
        package_metadata = [
            item for item in package_metadata
            if not item.model_name == result_bundle.model_name
            and item.model_name in app_properties.allowed_model_names
        ]

        # Add new to existing package metadata entries, i.e. under PACKAGE_NAME
        package_metadata.append(
            MetadataEntry(
                image_id=image_data.image_id,
                model_name=result_bundle.model_name,
                api_version=app_properties.app_version,
                iteration_publish_name=result_bundle.iteration_publish_name,
                execution_utctime=str(datetime.utcnow()),
                predictions=result_bundle.predictions))

        # Put all metadata in one dictionary
        metadata = {
            **{
                app_properties.app_name:
                json.dumps([_.to_dict() for _ in package_metadata])
            },
            **result_bundle.other_metadata
        }

        update_request = UpdateMetadataRequest(
            image_id=image_data.image_id,
            additional_metadata=metadata,
            plugin_id=plugin_id,
            e_tag=image_data.etag,
            skip_e_tag_validation=True,
            client_name=app_properties.client_name)
        louvre_client.update_image_metadata(update_request=update_request)

    @staticmethod
    def _get_package_metadata_entries_from_image_data(
            image_data: ImageData, app_name: str) -> List[MetadataEntry]:

        result: List[MetadataEntry] = []
        metadata = [
            item for item in image_data.metadata if app_name in item.keys()
        ]

        # Assume that metadata is a list of dictionaries with serialised values
        if not metadata or not isinstance(metadata[0], dict):
            return []
        try:
            entries = json.loads(metadata[0].get(app_name, None))

            # Assume that entries is a list of dictionaries
            if not entries or not isinstance(entries, list):
                return []

            # Parse each dictionary
            for entry in [_ for _ in entries if isinstance(_, dict)]:
                metadata_entry: MetadataEntry
                if not 'model_name' in entry.keys():
                    continue
                metadata_entry = MetadataUpdater._extract_metadata_entry_from_dict(
                    metadata_entry=entry, image_id=image_data.image_id)

                result.append(metadata_entry)

        except JSONDecodeError:
            pass

        return result

    @staticmethod
    def _extract_metadata_entry_from_dict(metadata_entry: Dict[str, Any],
                                          image_id: str) -> MetadataEntry:

        result = MetadataEntry(image_id=image_id,
                               model_name=metadata_entry['model_name'])

        if 'api_version' in metadata_entry.keys():
            result.api_version = metadata_entry['api_version']
        if 'iteration_publish_name' in metadata_entry.keys():
            result.iteration_publish_name = metadata_entry[
                'iteration_publish_name']
        if 'execution_utctime' in metadata_entry.keys():
            result.execution_utctime = metadata_entry['execution_utctime']
        if 'version' in metadata_entry.keys():
            _version = json.loads(metadata_entry['version'])
            if isinstance(_version, dict) and 'api_version' in _version.keys(
            ) and 'iteration_publish_name' in _version.keys():
                result.api_version = _version['api_version']
                result.iteration_publish_name = _version[
                    'iteration_publish_name']

        # Assume that predictions is in the right format, i.e. Dict[str, str]
        if 'predictions' in metadata_entry.keys():
            result.predictions = metadata_entry['predictions']

        return result

    @staticmethod
    def exists(image_data: ImageData,
               model_name: str,
               app_name: str,
               app_version: str,
               iteration_publish_name: Optional[str] = None) -> bool:
        """
        Return whether a metadata entry already exists.

        :param ImageData image_data: Image data with the image metadata
        :param str model_name: Model name to search for in the image metadata
        :param str app_name: App name to search for in the image metadata
        :param str app_version: App version to search for in the image metadata
        :param iteration_publish_name: Particular model to search for in the image metadata. Applies to Custom Vision models only. 
        :type iteration_publish_name: str | None

        :rtype: bool
        """
        entry = MetadataEntry(image_id=image_data.image_id,
                              model_name=model_name,
                              api_version=app_version,
                              iteration_publish_name=iteration_publish_name)
        existing = MetadataUpdater._get_package_metadata_entries_from_image_data(
            image_data, app_name=app_name)
        return entry in existing
