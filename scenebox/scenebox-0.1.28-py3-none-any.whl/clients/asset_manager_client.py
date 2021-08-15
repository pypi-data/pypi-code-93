#  Copyright (c) 2020 Caliber Data Labs.
#  All rights reserved.
#

import io
import json
import os
import re
import shutil
import tempfile
import time
from datetime import datetime
from os.path import exists, join
from typing import Dict, List, Optional, Union

import requests
from diskcache import Cache

from ..constants import (AUXILIARY_KEY, TIMESTAMP_FIELD, AssetsConstants,
                         JobConstants)
from ..custom_exceptions import (AssetError, IdentityError, InvalidAssetType,
                                 InvalidAuthorization, JobError,
                                 MetadataNotFoundError)
from ..models.object_access import ObjectAccess, ObjectAccessMedium
from ..tools import misc
from ..tools.logger import get_logger
from ..tools.misc import parse_file_path, retry
from ..tools.naming import standardize_name
from ..tools.time_utils import jsonify_metadata
from ..tools.misc import run_threaded

DEFAULT_SEARCH_SIZE = 50
DEFAULT_PAGINATION = 5000
PAUSE_TIME = 0.05

logger = get_logger(__name__)

VERSION_PATTERN = re.compile(r'/v\d+')
temp_dir = tempfile.TemporaryDirectory(dir='/tmp').name.split('/')[-2]
DEFAULT_CACHE_DIR = os.getenv('CACHE_DIR', temp_dir)
DEFAULT_CACHE_SIZE = os.getenv("CACHE_MAX_SIZE", 50)
DEFAULT_CACHE_SUB_DIR = "default"
DEFAULT_ORGANIZATION_SUB_DIR = 'default'


class AssetManagerClientCache(object):
    """File cache for assets fetched via the AssetManagerClient.

    Using the least-frequently-used eviction policy, the cache will fill
    until the size_limit_gb is reached and will begin eviction
    """

    def __init__(
            self,
            cache_size_gb: int = None,
            disabled: bool = False,
            asset_type: Optional[str] = None,
            identity: Optional[dict] = None
    ):

        if not cache_size_gb:
            cache_size_gb = DEFAULT_CACHE_SIZE

        self.cache_disabled = disabled
        self.cache_size_gb = int(cache_size_gb)

        # Initialized in the _set_cache method
        self.cache_location = None
        self.cache = None
        self._set_cache(asset_type=asset_type, identity=identity)

    def _get_cache_location(
            self,
            asset_type: Optional[str] = None,
            identity: Optional[dict] = None):
        # When not provided, defaults to <DEFAULT_CACHE_DIR,asset_type>.
        # If asset_type is None (for example, when initializing SceneEngineClient),
        # then defaults to a default sub directory.
        if asset_type:
            cache_location = os.path.join(DEFAULT_CACHE_DIR, asset_type)
        else:
            cache_location = os.path.join(
                DEFAULT_CACHE_DIR, DEFAULT_CACHE_SUB_DIR)

        organization = self._get_sanitized_organization_name(identity)
        cache_location = os.path.join(cache_location, organization)
        self.cache_location = cache_location
        return cache_location

    def _get_sanitized_organization_name(
            self,
            identity: Optional[dict] = None,
            replace_char: str = '_'):
        # Sanitize the organization name
        if identity:
            organization = identity.get('organization', '')
        else:
            organization = DEFAULT_ORGANIZATION_SUB_DIR
        organization = organization.lower()
        for symbol in [' ', '/', '\'', '\"', '(', ')']:
            organization = organization.replace(symbol, replace_char)
        return organization

    def _set_cache(
            self,
            asset_type: Optional[str] = None,
            identity: Optional[dict] = None) -> None:
        """Set the cache location.

        Args:
            asset_type (str): Asset type
            identity (dict): User identity dict
        """
        try:
            self.cache_location = self._get_cache_location(
                asset_type=asset_type, identity=identity)
            os.makedirs(self.cache_location, exist_ok=True)
        except Exception as e:
            logger.info(
                " cache_location ::: could not create {} because of {}, instead {} is created".format(
                    self.cache_location, e, temp_dir))
            self.cache_location = temp_dir
            os.makedirs(self.cache_location, exist_ok=True)

    def get_file_from_cache(self, key):
        if self.cache_disabled:
            return
        # Read a file as a File object
        with Cache(
                directory=self.cache_location,
                eviction_policy='least-frequently-used',
                size_limit=self.cache_size_gb * (2 ** 30)
        ) as ref:
            return ref.get(key, read=True)

    def put_file_into_cache(self, key, value):
        if self.cache_disabled:
            return
        # Put a file as a File object
        with Cache(
                directory=self.cache_location,
                eviction_policy='least-frequently-used',
                size_limit=self.cache_size_gb * (2 ** 30)
        ) as ref:
            return ref.set(key, value, read=True)

    def get_bytes_from_cache(self, key):
        if self.cache_disabled:
            return
        # Read a file as a bytes array
        with Cache(
                directory=self.cache_location,
                eviction_policy='least-frequently-used',
                size_limit=self.cache_size_gb * (2 ** 30)
        ) as ref:
            return ref.get(key, read=False)

    def put_bytes_into_cache(self, key, value):
        if self.cache_disabled:
            return
        with Cache(
                directory=self.cache_location,
                eviction_policy='least-frequently-used',
                size_limit=self.cache_size_gb * (2 ** 30)
        ) as ref:
            return ref.set(key, value, read=False)


class AssetManagerClient(AssetManagerClientCache):
    def __init__(
            self,
            asset_type: str = AssetsConstants.SESSIONS_ASSET_ID,  # default asset is session
            asset_manager_url: Optional[str] = None,
            metadata_only: bool = False,
            auth_token: Optional[str] = None,
            cache_disabled: bool = False,
            is_non_standard_asset: bool = False
    ):
        """Asset manager client for fetching/putting assets and metadata.

        :param asset_type: (str) The type of asset
        :param asset_manager_url: (str) The URL of the asset manager
        :param metadata_only: (bool) Whether to only return metadata
        :param auth_token: (str) Authentication token of the user -- must be provided
        :param cache_disabled: (bool): Disable caching; defaults to False
        :param is_non_standard_asset (bool): Whether the asset is a non-standard asset.
               If True, ignore asset-type checks.
        """

        if is_non_standard_asset is False and asset_type not in AssetsConstants.VALID_ASSETS:
            raise ValueError('Invalid asset_type `{}`'.format(asset_type))

        # Override enabled cache with env variable
        if misc.as_bool(os.environ.get("DISABLE_CACHING", False)):
            cache_disabled = True

        self.is_non_standard_asset = is_non_standard_asset

        if asset_manager_url is None:
            raise AssetError('asset_manager_url must be provided')
        self.asset_manager_url = asset_manager_url
        self.jobs_namespace_url = join(asset_manager_url, "jobs")
        self.assets_namespace_url = join(asset_manager_url, "assets")

        self.auth_token = auth_token
        if self.auth_token:
            self.identity = self._get_identity()
        else:
            self.identity = None

        self._set_asset_state(
            asset_type=asset_type,
            metadata_only=metadata_only)

        super().__init__(
            asset_type=asset_type,
            cache_size_gb=DEFAULT_CACHE_SIZE,
            disabled=cache_disabled,
            identity=self.identity
        )

    def _get_identity(
            self,
            wait_for_connection: bool = True,
            max_wait_time: int = 60):
        env_user_identity = os.getenv('SCENEBOX_USER_IDENTITY')
        if env_user_identity:
            # TODO: This is a temporary fix and should be improved
            return json.loads(env_user_identity)
        else:
            if self.auth_token is None:
                raise IdentityError(
                    'Cannot get identity when no auth has been provided')
            params = {}
            if self.auth_token:
                params['token'] = self.auth_token

            # Strip version from asset manager URL
            version_match = re.search(VERSION_PATTERN, self.asset_manager_url)
            if version_match:
                version = version_match.group()
                root_url = self.asset_manager_url.split(version)[0]
            else:
                root_url = self.asset_manager_url

            wait_time = 0
            sleep_time = 5
            while True:
                try:
                    resp = requests.get(
                        os.path.join(
                            root_url,
                            'auth'),
                        params=params)
                    break
                except requests.exceptions.ConnectionError as e:
                    if not wait_for_connection or wait_time > max_wait_time:
                        raise e
                    else:
                        logger.warning(
                            "could not connect to {}, retrying in {} seconds".format(
                                root_url, sleep_time))
                        time.sleep(sleep_time)
                        wait_time = wait_time + sleep_time
            if not resp.ok:
                raise IdentityError(
                    "Could not obtain the user identity {}", resp.content)
            return resp.json()

    def _set_asset_state(
            self,
            asset_type: str,
            metadata_only: bool
    ):
        if asset_type not in AssetsConstants.VALID_ASSETS:
            raise InvalidAssetType(
                "The asset type {} is invalid. Valid types are: {}".format(
                    asset_type, AssetsConstants.VALID_ASSETS))

        if not isinstance(metadata_only, bool):
            raise ValueError("metadata_only must be a boolean")

        self.asset_type = asset_type

        if asset_type in AssetsConstants.METADATA_ONLY_ASSETS:
            self.metadata_only = True
        else:
            self.metadata_only = metadata_only

        if metadata_only is False:
            self._set_cache(asset_type=asset_type, identity=self.identity)
        return self

    def add_asset_manager_params(
            self, params_dict: Optional[dict] = None) -> dict:

        if self.auth_token is None:
            raise InvalidAuthorization(
                "No authorization is provided in AssetManagerClient")

        params_dict = params_dict or {}
        params_dict['asset_type'] = self.asset_type
        params_dict['metadata_only'] = self.metadata_only
        if self.auth_token:
            params_dict['token'] = self.auth_token
        return params_dict

    def with_auth(self,
                  auth_token: Optional[str] = None,
                  ):
        if auth_token:
            self.auth_token = auth_token

        self.identity = self._get_identity()
        self._set_cache(asset_type=self.asset_type, identity=self.identity)
        return self

    def register_field(self, field_dict: dict):
        url = self.get_assets_url('register_field/')
        params = self.add_asset_manager_params({})
        resp = requests.post(
            url,
            json=field_dict,
            params=params)
        if not resp.ok:
            raise AssetError(
                'Could not register the field ::: {} -- {} -- {}'.format(
                    self.asset_type, resp.reason, resp.content))
        return resp.json()

    def delete(
            self,
            id: str,
            wait_for_deletion: bool = True) -> dict:

        id = self._check_identifier(id)
        url = self.get_assets_url(id)
        params = self.add_asset_manager_params({})
        resp = requests.delete(url, params=params)

        if not resp.ok:
            raise AssetError(
                'Could not delete the file ::: {} -- {} -- {}'.format(
                    self.asset_type, resp.reason, resp.content))

        if wait_for_deletion:
            self._wait_for_non_existence(id)

        return resp.json()

    def put_directory(self,
                      directory_path: str,
                      metadata: dict,
                      temp_dir=temp_dir) -> str:
        """Convert a directory to a zipfile and upload."""
        if not os.path.exists(directory_path):
            raise IOError('Path does not exist')

        with tempfile.NamedTemporaryFile(dir=temp_dir) as f:
            zip_ext = 'zip'
            temp_zipfile_path = f.name
            shutil.make_archive(temp_zipfile_path, zip_ext, directory_path)

            return self.put_asset(
                file_path=temp_zipfile_path,
                metadata=metadata,
                id="{}.{}".format(temp_zipfile_path, zip_ext),
                wait_for_completion=True)

    def put_file(
            self,
            file_object: Union[io.BytesIO, bytes, str],
            id: Optional[str] = None,
            corr_asset_id: Optional[str] = None,
            corr_asset_type: Optional[str] = None,
            wait_for_completion=False) -> str:
        """ Register and upload a file with the asset manager
        Args:
            file (BytesIO or bytes): bytes object
            id (str): the uid of the file. If not provided, will be set automatically
            corr_asset_id: this is only used when we are creating an additional file for an asset that already
                           exists (say creating thumbnails for an existing image/video). This is only used for
                           getting the file owner
            corr_asset_type: this is only used when we are creating an additional file for an asset that already
                           exists (say creating thumbnails for an existing image/video). This is only used for
                           getting the file owner
            wait_for_completion (bool): Whether to wait for the upload to finish before returning
        :return: id of the file
        """

        id = id or misc.get_guid()

        if isinstance(file_object, (io.BytesIO, io.IOBase)):
            file_object.seek(0)
            file = file_object.read()
        elif isinstance(file_object, str):
            file = file_object.encode("utf-8")
        else:
            file = file_object

        upload_params = self.get_temporary_upload_url(
            ids=[id],
            corr_asset_id=corr_asset_id,
            corr_asset_type=corr_asset_type)
        upload_url = upload_params[id]["url"]
        files = upload_params[id]["fields"]
        files["file"] = file
        #logger.debug("Upload URL: {}".format(upload_url))
        resp = requests.post(upload_url, files=files)
        if not resp.ok:
            raise AssetError(
                'Could not put the file ::: {} -- {} -- {}'.format(
                    self.asset_type, resp.reason, resp.content))

        return id

    def get_url(self,
                id: str) -> str:
        id = self._check_identifier(id)
        url = self.get_assets_url(id)
        params = self.add_asset_manager_params({"return_url": True})
        resp = requests.get(url, params=params)
        if not resp.ok:
            raise AssetError(
                'Could not get the file ::: {} -- {} -- {}'.format(
                    self.asset_type, resp.reason, resp.content))
        return resp.json()['url']

    def get_bytes(self,
                  id: str) -> bytes:
        id = self._check_identifier(id)
        # Check if the response object exists locally in the cache
        data_bytes = self.get_bytes_from_cache(id)

        if not data_bytes:
            self._check_storage()
            url = self.get_assets_url(id)
            params = self.add_asset_manager_params({"return_url": False})
            resp = requests.get(url, params=params)
            if not resp.ok:
                raise AssetError(
                    'Could not get the file ::: {} -- {} -- {}'.format(
                        self.asset_type, resp.reason, resp.content))
            data_bytes = resp.content
            self.put_bytes_into_cache(id, data_bytes)

        return data_bytes

    def get_bytes_in_batch(self,
                           ids: List[str]) -> Dict[str, bytes]:
        data_id_bytes_map = {}

        def threaded_get_bytes_and_append(id: str):
            data_id_bytes_map[id] = self.get_bytes(id)

        run_threaded(func=threaded_get_bytes_and_append,
                     iterable=ids,
                     desc="get bytes")

        return data_id_bytes_map

    def get_url_in_batch(self,
                         ids: List[str]) -> Dict[str, str]:
        id_url_map = {}

        def threaded_get_url_and_append(id: str):
            id_url_map[id] = self.get_url(id)

        run_threaded(func=threaded_get_url_and_append,
                     iterable=ids,
                     desc="get urls")

        return id_url_map

    def get_file_and_write(self,
                           id: str,
                           write_filepath: Optional[str] = None) -> str:

        bytesio_data = io.BytesIO(self.get_bytes(id=id))
        if not write_filepath:
            write_filepath = tempfile.NamedTemporaryFile(delete=False).name
        with open(write_filepath, 'wb') as fout:
            fout.write(bytesio_data.read())

        return write_filepath

    def exists(self,
               id: str) -> bool:
        id = self._check_identifier(id)
        url = self.get_assets_url('exists/{}'.format(id))
        params = self.add_asset_manager_params()
        resp = requests.get(url, params=params)
        if not resp.ok:
            raise AssetError(
                'Could not find the identifier ::: {} -- {} -- {}'.format(
                    self.asset_type, resp.reason, resp.content))
        return misc.as_bool(resp.json())

    def copy(self,
             id: str,
             new_id: str):
        id = self._check_identifier(id)
        url = self.get_assets_url('copy/{}'.format(id))
        params = self.add_asset_manager_params({"new_id": new_id})
        resp = requests.put(url, params=params)
        if not resp.ok:
            raise AssetError(
                'Could not copy the identifier {} to {} ::: {} -- {} -- {}'.format(
                    id, new_id, self.asset_type, resp.reason, resp.content))
        return resp.json()

    def count(self, search_dic: Optional[dict] = None) -> int:
        url = self.get_assets_url('count/')
        params = self.add_asset_manager_params()
        search_dic = search_dic or {}
        resp = requests.post(
            url,
            json=search_dic,
            params=params)
        if not resp.ok:
            raise AssetError(
                'Could not count the files::: {} -- {} -- {}'.format(
                    self.asset_type, resp.reason, resp.content))
        return resp.json()

    def average(self, field_name: str, search: Optional[dict] = None) -> float:
        if not field_name:
            raise ValueError(
                "field_name must be provided, {} is given".format(field_name))
        url = self.get_assets_url('average/')
        params = self.add_asset_manager_params()
        search = search or {}
        average_request = {
            'search': search,
            'field_name': field_name
        }
        resp = requests.post(
            url,
            json=average_request,
            params=params)
        if not resp.ok:
            raise AssetError(
                'Could not obtain average for field {} ::: {} -- {} -- {}'.format(
                    field_name, self.asset_type, resp.reason, resp.content))
        return resp.json()

    @retry(Exception, logger=logger)
    def get_metadata(self, id: str,
                     retry: bool = False) -> dict:
        id = self._check_identifier(id)
        url = self.get_assets_url('meta/{}'.format(id))
        params = self.add_asset_manager_params()
        resp = requests.get(url, params=params)
        if not resp.ok:
            raise MetadataNotFoundError(
                'Could not get the metadata from the identifier ::: {} -- {} -- {} -- {}'.format(
                    id, self.asset_type, resp.reason, resp.content))
        return resp.json()

    @retry(Exception, logger=logger)
    def put_asset(self,
                  metadata: dict,
                  file_path: Optional[str] = None,
                  filename: Optional[str] = None,
                  file_object: Optional[Union[io.BytesIO, bytes, str]] = None,
                  url: Optional[str] = None,
                  id: Optional[str] = None,
                  uri: Optional[str] = None,
                  geo_field: Optional[str] = None,
                  buffered_write: bool = False,
                  wait_for_completion: bool = True,
                  retry: bool = False) -> str:

        # metadata should be always provided
        # either of the following should be provided if the asset is not metadata only
        # url
        # file_path
        # file_object and filename

        id = id or misc.get_guid()
        metadata["id"] = id

        if not metadata.get(TIMESTAMP_FIELD):
            metadata[TIMESTAMP_FIELD] = datetime.utcnow()

        if self.asset_type in AssetsConstants.METADATA_ONLY_ASSETS:
            if any([filename, file_path, url, file_path, uri]):
                raise AssetError(
                    "asset {} does not accept file, filename, file_path, uri or, url".format(
                        self.asset_type))
        else:
            if not any([file_object, url, file_path, uri]) and self.asset_type != AssetsConstants.ANNOTATIONS_ASSET_ID:
                raise AssetError(
                    "file_object, url, file_path is required for asset {}".format(
                        self.asset_type))
            object_access = None
            if url:
                object_access = ObjectAccess(url=url,
                                             id=id,
                                             filename=filename)
                if uri:
                    raise AssetError(
                        "url {} cannot support uri".format(url))
            elif uri:
                object_access = ObjectAccess(uri=uri,
                                             id=id,
                                             filename=filename)
                if url:
                    raise AssetError(
                        "uri {} cannot support url".format(uri))
            elif file_path or file_object:
                if file_path:
                    if not exists(file_path):
                        raise AssetError(
                            "file_path {} does not exist".format(file_path))
                    filename, _, _, _ = parse_file_path(file_path)
                    file_object = open(file_path, 'rb')
                else:
                    filename = filename or id

                self.put_file(file_object=file_object, id=id)

                object_access = ObjectAccess(id=id, filename=filename)
            if object_access:
                metadata["object_access"] = object_access.to_dic()
        metadata_json = jsonify_metadata(metadata)

        params = {
            "replace": True,
            "geo_field": geo_field,
            "buffered_write": buffered_write,
            "replace_sets": False}
        params = self.add_asset_manager_params(params)
        resp = requests.put(
            url=self.get_assets_url("meta/{}".format(id)),
            json=metadata_json,
            params=params)

        if not resp.ok:
            raise AssetError(
                'Could not put the metadata for the identifier ::: {} -- {} -- {}'.format(
                    self.asset_type, resp.reason, resp.content))

        if wait_for_completion:
            self._wait_for_existence(id)
        return id

    @retry(Exception, logger=logger)
    def update_metadata(
            self,
            id: str,
            metadata: dict,
            buffered_write: bool = False,
            replace_sets: bool = False,
            retry: bool = False) -> dict:

        id = self._check_identifier(id)
        url = self.get_assets_url('meta/{}'.format(id))
        params = {"replace": False,
                  "replace_sets": replace_sets,
                  "buffered_write": buffered_write,
                  }
        params = self.add_asset_manager_params(params)
        metadata_json = jsonify_metadata(metadata)

        resp = requests.put(
            url,
            json=metadata_json,
            params=params)
        if not resp.ok:
            raise AssetError(
                'Could not update the metadata for the identifier ::: {} -- {} -- {}'.format(
                    self.asset_type, resp.reason, resp.content))
        return resp.json()

    def upsert_metadata(
            self,
            id: str,
            metadata: dict,
            buffered_write: bool = False,) -> dict:
        id = self._check_identifier(id)
        url = self.get_assets_url('meta/{}'.format(id))
        params = {"replace": True,
                  "replace_sets": True,
                  "buffered_write": buffered_write
                  }
        params = self.add_asset_manager_params(params)
        metadata_json = jsonify_metadata(metadata)

        resp = requests.put(
            url,
            json=metadata_json,
            params=params)
        if not resp.ok:
            raise AssetError(
                'Could not upsert the metadata for the identifier ::: {} -- {} -- {}'.format(
                    self.asset_type, resp.reason, resp.content))
        return resp.json()

    def search_assets(
            self,
            query: Optional[dict] = None,
            filters: Optional[dict] = None,
            size: int = DEFAULT_SEARCH_SIZE,
            offset: int = 0,
            sort_field: Optional[str] = None,
            sort_order: Optional[str] = None,
            scan: bool = False) -> List[str]:
        query = self._construct_query(query, filters)
        params = {'size': size, 'offset': offset, 'scan': scan}
        if sort_field:
            params['sort_field'] = sort_field
        if sort_order:
            params['sort_order'] = sort_order
        url = self.get_assets_url('')
        params = self.add_asset_manager_params(params)
        resp = requests.post(url, json=query, params=params)
        if not resp.ok:
            raise AssetError(
                'Could not search the files ::: {} -- {} -- {}'.format(
                    self.asset_type, resp.reason, resp.content))
        return resp.json()['results']

    def search_assets_large(
            self,
            query: Optional[dict] = None,
            filters: Optional[dict] = None
    ) -> List[str]:
        query = self._construct_query(query, filters)
        params = {"size": DEFAULT_PAGINATION,
                  "offset": 0,
                  "scan": False,
                  "sort_field": "id",
                  "sort_order": "asc"
                  }
        url = self.get_assets_url('')
        params = self.add_asset_manager_params(params)
        resp = requests.post(url, json=query, params=params)
        if not resp.ok:
            raise AssetError(
                'Could not search the files ::: {} -- {} -- {}'.format(
                    self.asset_type, resp.reason, resp.content))
        results = resp.json().get('results')
        if results:
            search_after = resp.json()['results'][-1]
        else:
            return results
        while search_after:
            params = {"size": DEFAULT_PAGINATION,
                      "offset": 0,
                      "scan": False,
                      "sort_field": "id",
                      "sort_order": "asc",
                      "search_after": search_after
                      }
            url = self.get_assets_url('')
            params = self.add_asset_manager_params(params)
            resp = requests.post(url, json=query, params=params)
            if not resp.ok:
                raise AssetError(
                    'Could not search the files ::: {} -- {} -- {}'.format(
                        self.asset_type, resp.reason, resp.content))
            if resp.json().get('results'):
                res = resp.json()['results']
                results += res
                search_after = res[-1]
            else:
                break
        return results

    def remove_with_query(self,
                          query: Optional[dict] = None,
                          filters: Optional[dict] = None,
                          wait_for_completion: bool = False) -> str:
        query = self._construct_query(query, filters)
        params = self.add_asset_manager_params()
        url = self.get_assets_url('remove_with_query/')
        resp = requests.post(url, json=query, params=params)
        if not resp.ok:
            raise AssetError(
                'Could not remove the assets ::: {} -- {} -- {}'.format(
                    self.asset_type, resp.reason, resp.content))
        job_id = resp.json()['job_id']
        if wait_for_completion:
            self._wait_for_job_completion(job_id)

        return job_id

    def remove_with_list(self,
                         assets_list: Optional[list] = None,
                         wait_for_completion: bool = False) -> str:
        assets_list = assets_list or []
        params = self.add_asset_manager_params()
        url = self.get_assets_url('remove_with_list/')
        resp = requests.post(
            url,
            json={
                "assets_list": assets_list},
            params=params)
        if not resp.ok:
            raise AssetError(
                'Could not remove the assets ::: {} -- {} -- {}'.format(
                    self.asset_type, resp.reason, resp.content))

        job_id = resp.json()['job_id']
        if wait_for_completion:
            self._wait_for_job_completion(job_id)

        return job_id

    def search_meta(
            self,
            query=None,
            size=DEFAULT_SEARCH_SIZE,
            filters: Optional[dict] = None,
            offset=0,
            sort_field=None,
            sort_order=None,
            scan=False):
        query = self._construct_query(query, filters)
        params = {'size': size, 'offset': offset, 'scan': scan}
        if sort_field:
            params['sort_field'] = sort_field
        if sort_order:
            params['sort_order'] = sort_order
        url = self.get_assets_url('meta')
        params = self.add_asset_manager_params(params)
        resp = requests.post(url, json=query, params=params)
        if not resp.ok:
            raise AssetError(
                'Could not search the metadata ::: {} -- {} -- {}'.format(
                    self.asset_type, resp.reason, resp.content))
        return resp.json()

    def search_meta_large(
            self,
            query: Optional[dict] = None,
            filters: Optional[dict] = None):
        query = self._construct_query(query, filters)
        params = {"size": DEFAULT_PAGINATION,
                  "offset": 0,
                  "scan": False,
                  "sort_field": "id",
                  "sort_order": "asc"
                  }
        url = self.get_assets_url('meta')
        params = self.add_asset_manager_params(params)
        resp = requests.post(url, json=query, params=params)
        if not resp.ok:
            raise AssetError(
                'Could not search the files ::: {} -- {} -- {}'.format(
                    self.asset_type, resp.reason, resp.content))
        results = resp.json()
        if results:
            search_after = resp.json()[-1]['id']
        else:
            return results
        while search_after:
            params = {"size": DEFAULT_PAGINATION,
                      "offset": 0,
                      "scan": False,
                      "sort_field": "id",
                      "sort_order": "asc",
                      "search_after": search_after
                      }
            url = self.get_assets_url('meta')
            params = self.add_asset_manager_params(params)
            resp = requests.post(url, json=query, params=params)
            if not resp.ok:
                raise AssetError(
                    'Could not search the files ::: {} -- {} -- {}'.format(
                        self.asset_type, resp.reason, resp.content))
            if resp.json():
                res = resp.json()
                results += res
                search_after = res[-1]['id']
            else:
                break
        return results

    def summary_meta(self, summary_request):
        url = self.get_assets_url('meta/summary/')
        params = self.add_asset_manager_params()
        resp = requests.post(
            url,
            json=summary_request,
            params=params)
        if not resp.ok:
            raise AssetError(
                'Could not retrieve the metadata summary ::: {} -- {} -- {}'.format(
                    self.asset_type, resp.reason, resp.content))
        return resp.json()

    def summary_2d(self, summary_2d_request):
        url = self.get_assets_url('summary_2d/')
        params = self.add_asset_manager_params()
        resp = requests.post(
            url,
            json=summary_2d_request,
            params=params)
        if not resp.ok:
            raise AssetError(
                'Could not get the confusion matrix for ::: {} -- {} -- {}'.format(
                    summary_2d_request, resp.reason, resp.content))
        return resp.json()

    def api_status(self):
        url = self.get_assets_url('status/')
        params = self.add_asset_manager_params()
        resp = requests.get(url, params=params)
        if not resp.ok:
            raise AssetError(
                'Could not check the status of the API ::: {} -- {} -- {}'.format(
                    self.asset_type, resp.reason, resp.content))

    def get_assets_url(self, route=""):
        url = join(self.assets_namespace_url, route)
        return url

    def get_statistics(self, field_dicts: List[dict]):
        statistics_endpoint = self.get_assets_url("field_statistics/")
        params = self.add_asset_manager_params()
        resp = requests.post(
            statistics_endpoint,
            params=params,
            json={
                'field_dicts': field_dicts})
        if not resp.ok:
            raise AssetError(
                'Could not get field statistics ::: {} -- {} -- {}'.format(
                    self.asset_type, resp.reason, resp.content))
        return resp.json()

    def _get_job_status(self, job_id):
        """Get the status of the async job.

        Assumes that the job_id is the same as the celery task_id

        :param job_id: Celery task ID
        :return:
        """
        status_endpoint = os.path.join(
            self.jobs_namespace_url, "status", job_id)
        params = {}
        if self.auth_token:
            params['token'] = self.auth_token
        resp = requests.get(status_endpoint, params=params)
        status = resp.json().get('status')
        return status

    def _wait_for_job_completion(self, job_id):
        while True:
            status = self._get_job_status(job_id)
            if status == JobConstants.STATUS_FINISHED:
                break
            elif status in {JobConstants.STATUS_CANCELLED, JobConstants.STATUS_ABORTED}:
                job_metadata = self.with_asset_state(
                    'jobs', True).get_metadata(job_id)
                job_notes = job_metadata['notes']
                raise JobError(
                    'Job {} encountered error with status {} with notes::: {}'.format(
                        job_id, status, job_notes))
            else:
                time.sleep(1)

    def _wait_for_existence(self, id):
        id = self._check_identifier(id)
        while not self.exists(id):
            time.sleep(PAUSE_TIME)

    def _wait_for_non_existence(self, id):
        id = self._check_identifier(id)
        while self.exists(id):
            time.sleep(PAUSE_TIME)

    def _check_storage(self):
        if self.metadata_only:
            raise AssetError('Asset client is metadata only')

    def update_asset_state(self, asset_type: str, metadata_only: bool = False):

        if self.is_non_standard_asset is False and asset_type not in AssetsConstants.VALID_ASSETS:
            raise InvalidAssetType(
                "The asset type {} is invalid. Valid types are: {}".format(
                    asset_type, AssetsConstants.VALID_ASSETS))

        if not isinstance(metadata_only, bool):
            raise ValueError("metadata_only must be a boolean")

        self.asset_type = asset_type
        if asset_type in AssetsConstants.METADATA_ONLY_ASSETS:
            self.metadata_only = True
        else:
            self.metadata_only = metadata_only

    def with_asset_state(self, asset_type: str, metadata_only: bool = False):
        """Set the asset state, for use in chaining.

        Eg. client.with_asset_state("images", True).search_files({})
        """

        self.update_asset_state(
            asset_type=asset_type,
            metadata_only=metadata_only)
        return self

    def _construct_query(self,
                         query: Optional[Dict],
                         filters: Optional[Dict]):
        if query is None:
            query = {}
        elif not isinstance(query, dict):
            raise ValueError('Query parameter must be a dictionary')

        if filters:
            query_filters = query.get("filters", [])
            for key, value in filters.items():
                if isinstance(value, list):
                    query_filters.append({"field": key, "values": value})
                else:
                    query_filters.append({"field": key, "values": [value]})
            query["filters"] = query_filters
        return query

    def _check_identifier(self, id: str) -> str:
        # Perform any preprocessing on the identifier
        if self.asset_type == AssetsConstants.SESSIONS_ASSET_ID:
            id = standardize_name(id)
        return id

    def download_data_with_query(self,
                                 destination_dir: str,
                                 query: Optional[dict] = None,
                                 download_metadata=True) -> dict:

        if not os.path.isdir(destination_dir):
            raise NotADirectoryError(
                "{} does not exist".format(destination_dir))

        ids = self.search_assets(
            query=query, scan=True)

        local_dataset = {}

        def threaded_download_asset_and_metadata(id: str):
            logger.info(
                "downloading binary and metadata for {}".format(id))
            local_access = {}
            if not self.metadata_only:
                filepath = os.path.join(destination_dir, id)
                self.get_file_and_write(id=id, write_filepath=filepath)
                local_access["filepath"] = filepath
            if download_metadata:
                metadata = self.get_metadata(id=id)
                local_access["metadata"] = metadata
                json_filepath = os.path.join(
                    destination_dir, '{}.json'.format(id))
                with open(json_filepath, 'w') as file:
                    file.write(json.dumps(metadata))

            local_dataset[id] = local_access

        run_threaded(func=threaded_download_asset_and_metadata,
                     iterable=ids,
                     desc="download data with query")

        return local_dataset

    def get_temporary_upload_url(self,
                                 ids: List[str],
                                 corr_asset_id: Optional[str] = None,
                                 corr_asset_type: Optional[str] = None,
                                 ) -> Dict:
        params = self.add_asset_manager_params()
        body = {"ids": ids}

        if corr_asset_id:
            body["corr_asset_id"] = corr_asset_id

        if corr_asset_type:
            body["corr_asset_type"] = corr_asset_type

        resp = requests.post(
            self.get_assets_url('temporary_upload_url/'),
            json=body,
            params=params)
        if not resp.ok:
            raise AssetError(
                'Could not get temporary upload url::: {} -- {} -- {}'.format(
                    self.asset_type, resp.reason, resp.content))
        return resp.json()

    def get_storage_url(self,
                        ids: List[str],
                        corr_asset_id: Optional[str] = None,
                        corr_asset_type: Optional[str] = None,
                        ) -> Dict:
        params = self.add_asset_manager_params()
        body = {"ids": ids}

        if corr_asset_id:
            body["corr_asset_id"] = corr_asset_id

        if corr_asset_type:
            body["corr_asset_type"] = corr_asset_type

        resp = requests.post(
            self.get_assets_url('storage_url/'),
            json=body,
            params=params)
        if not resp.ok:
            raise AssetError(
                'Could not get storage url::: {} -- {} -- {}'.format(
                    self.asset_type, resp.reason, resp.content))
        return resp.json()

    def get_auxiliary_search_fields(self) -> List[dict]:
        resp = requests.get(
            self.get_assets_url("meta/search_fields/"),
            params=self.add_asset_manager_params()
        )
        if not resp.ok:
            raise AssetError(
                'Could not get search fields::: {} -- {} -- {}'.format(
                    self.asset_type, resp.reason, resp.content))
        return [
            d for d in resp.json() if d['field'].startswith(
                AUXILIARY_KEY + ".")]

    def get_url_from_object_access(self,
                                   object_access: ObjectAccess,
                                   corr_id: Optional[str] = None) -> str:

        if object_access.url:
            return object_access.url

        params = self.add_asset_manager_params()
        body = object_access.to_dic()
        if corr_id:
            body["corr_id"] = corr_id
        resp = requests.post(
            self.get_assets_url('url_from_object_access/'),
            json=body,
            params=params
        )
        if not resp.ok:
            raise AssetError('Could not get url for {}::: {} -- {} -- {}'.format(
                object_access.to_dic(), self.asset_type, resp.reason, resp.content))

        return resp.json()["url"]

    def get_bytes_from_object_access(self,
                                     object_access: ObjectAccess,
                                     corr_id: Optional[str] = None) -> bytes:

        url = self.get_url_from_object_access(
            object_access=object_access, corr_id=corr_id)

        resp = requests.get(url)
        if not resp.ok:
            raise AssetError(
                'Could not get url ::: {} -- {} -- {}'.format(
                    self.asset_type, resp.reason, resp.content))
        return resp.content

    def add_auxiliary(self,
                      id: str,
                      auxiliary: dict) -> dict:

        if self.exists(id=id):
            metadata = {AUXILIARY_KEY: auxiliary}
            self.update_metadata(id=id,
                                 metadata=metadata,
                                 replace_sets=False)

            return metadata
        else:
            raise AssetError("asset id {} not found".format(id))

    def add_auxiliary_batch(self, id_auxiliary_map: Dict[str, dict]):

        run_threaded(func=self.add_auxiliary,
                     iterable=id_auxiliary_map.items(),
                     desc="add auxiliary batch")
