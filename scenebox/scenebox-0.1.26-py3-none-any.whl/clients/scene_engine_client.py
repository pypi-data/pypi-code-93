#  Copyright (c) 2020 Caliber Data Labs.
#  All rights reserved.
#
import io
import json
import os
import re
import time
from collections import defaultdict
from datetime import datetime, timedelta
from os.path import join
from typing import Dict, Iterable, List, Optional, Tuple, Type, Union

import numpy as np
import requests
from deprecated import deprecated

from ..clients.job_manager_client import Job, wait_for_jobs
from ..constants import (AUXILIARY_KEY, TIMESTAMP_FIELD, AnnotationMediaTypes,
                         AssetsConstants, ConfigTypes, EntityInfluenceTypes,
                         EntityNames, EntityTypes, JobConstants, SessionTypes,
                         SetsAssets, SetTags)
from ..custom_exceptions import (AssetError, IndexingException,
                                 InvalidArgumentsError, InvalidTimeError,
                                 JobError, ResponseError, SetsError)
from ..models.annotation import Annotation
from ..models.enricher import Enricher
from ..models.object_access import ObjectAccess
from ..tools.image_utils import get_image_attributes
from ..tools.logger import get_logger
from ..tools.misc import (get_guid, get_md5_from_json_object,
                          hash_string_into_positive_integer_reproducible, parse_file_path,
                          run_threaded)
from ..tools.naming import UriParser, get_similarity_index_name
from ..tools.time_utils import (datetime_or_str_to_iso_utc,
                                str_or_datetime_to_datetime,
                                string_to_datetime)
from ..tools.video_utils import get_video_attributes
from .asset_manager_client import DEFAULT_SEARCH_SIZE, AssetManagerClient

DEFAULT_MAX_ASSETS = 250
VERSION_POSTFIX = "v1"
TIME_INDEX_FIELD = "time_index"

logger = get_logger(__name__)

try:
    import pandas as pd
    import dill as pickle
    from IPython.display import Javascript
except ImportError as e:
    logger.warning("Could not import packages: {}".format(e))


def no_set_provided_error():
    raise ValueError(
        "No set_id provided and no default set_id exists. Either provide or set with _use_set(<set_id>)")


def no_asset_provided_error():
    raise ValueError(
        "No asset_type provided and no default asset_type exists. Either provide or set with _set_asset_state("
        "<asset_type>, <metadata:only>)")


def invalid_set_asset_error(asset_type):
    raise ValueError(
        "The asset_type {} is not a valid set asset type. Valid set assets are: {}".format(
            asset_type, SetsAssets.VALID_ASSET_TYPES))


class SceneEngineClient(object):
    """Utility class for interacting with the SceneEngine programmatically.

    This class is intended to be used directly by the client
    Usage:
        - Interact with assets by setting:
            - asset_type
            - metadata_only
        - Special utility methods for interacting with sets and projects
            - Search for sets/projects
            - Search media within a set/project
            - Zip a set
            - Download all media within a set
    """

    def __init__(
            self,
            auth_token: Optional[str] = None,
            scene_engine_url: str = 'https://scene-engine.demo.scenebox.ai/',
            asset_manager_url: Optional[str] = None,
            artifacts_path: str = ".",
    ):
        self.scene_engine_url = scene_engine_url
        self._fix_scene_engine_url()
        self.set_id = None
        self.front_end_url = self.scene_engine_url.replace("scene-engine.", "").replace(VERSION_POSTFIX, "") if self.scene_engine_url else None
        self.project_id = None
        self.requests = SceneEngineRequestHandler(
            self.scene_engine_url, auth_token)

        self.amc_cache = {}

        self.asset_manager_url = asset_manager_url or self._get_asset_manager_url()
        self.auth_token = auth_token

        self.artifacts_path = artifacts_path

    def get_asset_manager_client(self, asset_type) -> AssetManagerClient:
        if asset_type not in self.amc_cache:
            self.amc_cache[asset_type] = AssetManagerClient(
                asset_type=asset_type,
                asset_manager_url=self.asset_manager_url,
                auth_token=self.auth_token)
        return self.amc_cache[asset_type]

    def _fix_scene_engine_url(self):
        if not self.scene_engine_url:
            return
        if self.scene_engine_url.endswith("/{}".format(VERSION_POSTFIX)):
            pass
        elif self.scene_engine_url.endswith("/{}/".format(VERSION_POSTFIX)):
            self.scene_engine_url = self.scene_engine_url[:-1]
        elif self.scene_engine_url.endswith("/"):
            self.scene_engine_url += VERSION_POSTFIX
        else:
            self.scene_engine_url += "/{}".format(VERSION_POSTFIX)

    def _get_asset_manager_url(self) -> str:
        resp = self.requests.get("status", remove_version=True)
        resp.raise_for_status()

        version = resp.json().get("asset_manager_url")
        if version is None:
            ValueError("cannot get asset_manager_url")
        return version

    def with_auth(self,
                  auth_token: Optional[str] = None,
                  ):
        if auth_token:
            self.auth_token = auth_token

        # Need to also call with_auth of AssetManagerClient in order
        # to update the asset cache

        self.requests.with_auth(
            auth_token=auth_token)

        return self

    def get_version(self) -> str:
        """
        get the version of the SceneBox platform
        :return: version number
        """
        resp = self.requests.get("status", remove_version=True)
        resp.raise_for_status()

        version = resp.json().get("version")
        if version is None:
            ValueError("cannot get version")

        return version

    def get_state(self) -> str:
        """
        get the state of the SceneBox platform
        :return: state
        """
        resp = self.requests.get("status", remove_version=True)
        resp.raise_for_status()

        state = resp.json().get("state")
        if state is None:
            ValueError("cannot get version")

        return state

    def update_state(self, desired_state: str) -> bool:
        """update the state of the SceneBox platform."""
        options = {
            "state": desired_state
        }
        resp = self.requests.post("status", json=options, remove_version=True)
        resp.raise_for_status()

        return True

    def update_artifact_path(self, artifacts_path):
        self.artifacts_path = artifacts_path

    def get_job(self, job_id: str) -> Job:
        metadata = self.with_asset_state(
            AssetsConstants.JOBS_ASSET_ID).get_metadata(id=job_id)

        return Job(
            status=metadata.get("status"),
            id=job_id,
            progress=metadata.get("progress", 0.0),
            description=metadata.get("description")
        )

    def _wait_for_job_completion(self,
                                 job_id: str,
                                 increments_sec: int = 10,
                                 enable_max_wait: bool = False,
                                 max_wait_sec: int = 300):

        elapsed_time = 0
        while not enable_max_wait or elapsed_time < max_wait_sec:
            elapsed_time += increments_sec
            job = self.get_job(job_id=job_id)
            logger.info(
                "job_id {:40.40s}|Status:{:12.12s}|Progress:{:6.1f} Elapsed Time: {:5d} sec|Description: {} \r".format(
                    job_id,
                    job.status,
                    job.progress,
                    elapsed_time,
                    job.description))
            if job.status == JobConstants.STATUS_FINISHED:
                logger.info(150 * "-" + "\r")
                return
            elif job.status in {JobConstants.STATUS_CANCELLED, JobConstants.STATUS_ABORTED}:
                job_metadata = self.with_asset_state(
                    AssetsConstants.JOBS_ASSET_ID).get_metadata(job_id)
                job_notes = job_metadata['notes']
                raise JobError(
                    'Job {} encountered error with status {} with notes::: {}'.format(
                        job_id, job.status, job_notes))
            else:
                time.sleep(increments_sec)

        raise JobError(
            "Job {} is not finished after {} seconds".format(
                job_id, max_wait_sec))

    def _wait_for_operation_completion(self,
                                       operation_id: str,
                                       increments_sec: int = 10,
                                       enable_max_wait: bool = False,
                                       max_wait_sec: int = 300):

        elapsed_time = 0
        while not enable_max_wait or elapsed_time < max_wait_sec:
            elapsed_time += increments_sec
            operation_status = self.get_operation_status(operation_id)
            status = operation_status.get("status")
            progress = operation_status.get("progress")
            logger.info(
                "operation_id {:40.40s}|Status:{:12.12s}|Progress:{:6.1f} Elapsed Time: {:5d} sec\r".format(
                    operation_id,
                    status,
                    progress,
                    elapsed_time))
            if status == JobConstants.STATUS_FINISHED:
                logger.info(150 * "-" + "\r")
                return
            elif status in {JobConstants.STATUS_CANCELLED, JobConstants.STATUS_ABORTED}:
                raise JobError('Operation {} encountered error'.format(operation_id))
            else:
                time.sleep(increments_sec)

        raise JobError(
            "Operation {} is not finished after {} seconds".format(
                operation_id, max_wait_sec))

    @deprecated("use create_project instead")
    def create_annotation_project(
            self,
            project_id,
            name,
            description,
            labelling_requirements,
            provider,
            client_id=None,
            provider_auth_token=None,
            wait_for_completion=True):
        options = {
            "name": name,
            "description": description,
            "labelling_requirements": labelling_requirements
        }
        headers = {
            "client_id": client_id,
            "auth_token": provider_auth_token
        }
        params = self.get_asset_manager_client(
            asset_type=AssetsConstants.ANNOTATION_PROJECTS_ASSET_ID).add_asset_manager_params(
            {
                "provider": provider})
        resp = self.requests.post(
            "annotation_projects/add/{}".format(project_id),
            trailing_slash=False,
            params=params,
            headers=headers,
            json=options)
        if not resp.ok:
            raise ResponseError(
                "Could not create the annotation project: {}".format(
                    resp.content))
        id = resp.json()["id"]
        if wait_for_completion:
            job_id = resp.json()["job_id"]
            self._wait_for_job_completion(job_id)
        return id

    def create_project(
            self,
            name: str,
            description: Optional[str] = None) -> str:
        options = {
            "name": name,
            "description": description
        }
        resp = self.requests.post(
            "projects/add/",
            trailing_slash=True,
            json=options)
        if not resp.ok:
            raise ResponseError(
                "Could not create the project: {}".format(
                    resp.content))

        id = resp.json()["id"]
        return id

    def delete_project(
            self,
            project_id: str):
        resp = self.requests.delete(
            "projects/meta/{}".format(project_id),
            trailing_slash=False)
        if not resp.ok:
            raise ResponseError(
                "Could not delete the project: {}".format(
                    resp.content))

    def create_operation(self,
                         name: str,
                         operation_type: str,
                         project_id: str,
                         config: dict,
                         stage: int = 0,
                         description: Optional[str] = None) -> str:
        options = {
            "name": name,
            "type": operation_type,
            "stage": stage,
            "project_id": project_id,
            "config": config,
            "description": description
        }

        resp = self.requests.post(
            "operations/add/",
            trailing_slash=True,
            json=options)
        if not resp.ok:
            raise ResponseError(
                "Could not create the operation: {}".format(
                    resp.content))

        id = resp.json()["id"]
        return id

    def delete_operation(self, operation_id: str):

        resp = self.requests.delete(
            "operations/{}".format(operation_id),
            trailing_slash=False)
        if not resp.ok:
            raise ResponseError(
                "Could not delete the operation: {}".format(
                    resp.content))

    def start_operation(
            self,
            operation_id: str,
            operation_stage: Optional[str]=None,
            wait_for_completion: bool = False) -> str:

        if operation_stage:
            params = {"operation_stage": operation_stage}
        else:
            params = None

        resp = self.requests.put(
            "operations/control/{}".format(operation_id),
            params=params,
            trailing_slash=False)
        if not resp.ok:
            raise ResponseError(
                "Could not delete the operation: {}".format(
                    resp.content))

        job_id = resp.json().get("job_id")

        if wait_for_completion:
            self._wait_for_operation_completion(operation_id)

        return job_id

    def get_operation_status(self, operation_id: str) -> dict:
        resp = self.requests.get("operations/{}/status/".format(operation_id))
        resp.raise_for_status()
        return resp.json()

    def add_sets_to_project(
            self,
            project_id: str,
            sets: List[str],
            stage: int = 0):
        options = {
            "sets": sets,
            "stage": stage,
        }

        resp = self.requests.post(
            "projects/{}/add_sets/".format(project_id),
            trailing_slash=True,
            json=options)
        resp.raise_for_status()

    def remove_sets_from_project(
            self,
            project_id: str,
            sets: List[str],
            stage: int = 0):
        options = {
            "sets": sets,
            "stage": stage,
        }

        resp = self.requests.post(
            "projects/{}/remove_sets/".format(project_id),
            trailing_slash=True,
            json=options)
        resp.raise_for_status()

    def create_set(
            self,
            name: str,
            asset_type: str,
            origin: Optional[str] = None,
            description: Optional[str] = None,
            expected_count: Optional[int] = None,
            tags: Optional[List[str]] = None,
            is_primary: bool = False,
            raise_if_set_exists=False,
    ) -> str:
        """Create a set."""
        same_name_sets = self.get_asset_manager_client(
            asset_type=AssetsConstants.SETS_ASSET_ID).search_assets(
            query={
                "filters": [
                    {
                        "field": "name",
                        "values": [name]}]})

        if same_name_sets:
            if raise_if_set_exists:
                raise SetsError("set name {} already exists".format(name))
            else:
                return same_name_sets[0]

        tags = tags or []

        if is_primary:
            tags.append(SetTags.PRIMARY_SET_TAG)

        options = {
            "assets_type": asset_type,
            "name": name,
            "description": description,
            "origin": origin,
            "expected_count": expected_count,
            "tags": tags or []
        }
        resp = self.requests.post(
            "sets/add/",
            trailing_slash=True,
            json=options)

        if not resp.ok:
            raise ResponseError(
                "Could not create the set: {}".format(
                    resp.content))

        id = resp.json()["id"]
        return id

    def create_annotation_instruction(
            self,
            name: str,
            key: str,
            annotator: str,
            annotation_type: str,
            payload: dict,
            media_type: str = AnnotationMediaTypes.IMAGE,
            description: Optional[str] = None) -> str:
        """Create an annotation_instruction."""
        options = {
            "name": name,
            "key": key,
            "annotator": annotator,
            "type": ConfigTypes.ANNOTATION_INSTRUCTION,
            "annotation_type": annotation_type,
            "config": payload,
            "media_type": media_type,
            "description": description,
        }
        resp = self.requests.post(
            "configs/add/",
            trailing_slash=True,
            json=options)

        if not resp.ok:
            raise ResponseError(
                "Could not create the annotation_instruction: {}".format(
                    resp.content))

        id = resp.json()["id"]
        return id

    def delete_annotation_instruction(self, annotation_instruction_id: str):

        resp = self.requests.delete(
            "configs/meta/{}".format(annotation_instruction_id),
            trailing_slash=False)
        if not resp.ok:
            raise ResponseError(
                "Could not delete the annotation_instruction: {}".format(
                    resp.content))

    def create_config(
            self,
            name: str,
            type: str,
            config: dict,
            description: Optional[str] = None,
            **kwarg) -> str:
        """Create a config."""
        options = kwarg
        options.update({
            "name": name,
            "type": type,
            "config": config,
            "description": description,
        })
        resp = self.requests.post(
            "configs/add/",
            trailing_slash=True,
            json=options)

        if not resp.ok:
            raise ResponseError(
                "Could not create the config: {}".format(
                    resp.content))

        id = resp.json()["id"]
        return id

    def delete_config(self, config_id: str):

        resp = self.requests.delete(
            "configs/meta/{}".format(config_id),
            trailing_slash=False)
        if not resp.ok:
            raise ResponseError(
                "Could not delete the config_id: {}".format(
                    resp.content))

    def get_config(self, config_id: str, complete_info=False) -> dict:

        resp = self.requests.get(
            "configs/meta/{}".format(config_id),
            trailing_slash=False)
        if not resp.ok:
            raise ResponseError(
                "Could not delete the config_id: {}".format(
                    resp.content))

        if complete_info:
            return resp.json()
        else:
            return resp.json().get("config", {})

    def set_lock(self, set_id: str) -> bool:
        resp = self.requests.put("sets/{}/lock".format(set_id))
        resp.raise_for_status()

        return True

    def set_unlock(self, set_id: str) -> bool:
        resp = self.requests.delete("sets/{}/lock".format(set_id))
        resp.raise_for_status()

        return True

    def set_is_locked(self, set_id: str) -> bool:
        resp = self.requests.get("sets/{}/lock".format(set_id))
        resp.raise_for_status()

        return resp.json().get("locked")

    def delete_set(
            self,
            set_id: str = None,
            wait_for_completion: bool = False) -> str:
        """Delete a set."""
        if not set_id and not self.set_id:
            no_set_provided_error()
        set_id = set_id or self.set_id
        resp = self.requests.delete("sets/{}".format(set_id))
        resp.raise_for_status()
        if wait_for_completion:
            job_id = resp.json()["job_id"]
            self._wait_for_job_completion(job_id)
        return resp.json().get("job_id")

    def get_set_status(self, set_id: str = None) -> dict:
        if not set_id and not self.set_id:
            no_set_provided_error()
        resp = self.requests.get("sets/{}/status/".format(set_id))
        resp.raise_for_status()
        return resp.json()

    def add_assets_to_set(
            self,
            query: Optional[dict] = None,
            ids: Optional[list] = None,
            set_id: Optional[str] = None,
            limit: Optional[int] = None,
            wait_for_availability: bool = True,
            timeout: int = 30,
            wait_for_completion: bool = False,
    ) -> str:
        """Add assets to a set either by query or by ids."""
        if not set_id and not self.set_id:
            no_set_provided_error()

        set_id = set_id or self.set_id
        if not set_id:
            raise ValueError("No default set available")

        if query is None and ids is None:
            raise ValueError(
                "Either a search query or a list of ids must be provided")

        if self.set_is_locked(set_id):
            if wait_for_availability:
                t_start = time.time()
                while True:
                    time.sleep(1)
                    if time.time() - t_start > timeout:
                        raise TimeoutError(
                            "Timeout waiting for set {} to unlock".format(set_id))
                    if not self.set_is_locked(set_id):
                        logger.info(
                            "Set {} is locked, waiting 1s to add assets".format(set_id))
                        break
            else:
                raise SetsError("Set {} is locked".format(set_id))

        if query is not None:
            if limit:
                params = {"limit": limit}
            else:
                params = None
            resp = self.requests.post(
                "sets/{}/add_assets_query/".format(set_id),
                trailing_slash=True,
                json=query,
                params=params)
        elif ids is not None:
            assets_payload = {"asset_list": ids}
            resp = self.requests.post(
                "sets/{}/add_assets_list/".format(set_id),
                trailing_slash=True,
                json=assets_payload)
        else:
            raise SetsError(
                "Either ids or query should be specified for sets addition")

        if not resp.ok:
            raise ResponseError(
                "Could not add assets to set: {}, {}".format(
                    resp.content, resp.reason))

        if wait_for_completion:
            job_id = resp.json()["job_id"]
            self._wait_for_job_completion(job_id)

        return resp.json().get("job_id")

    def remove_assets_from_set(
            self,
            query: Optional[dict] = None,
            ids: Optional[list] = None,
            set_id: Optional[str] = None,
            wait_for_availability: bool = True,
            timeout: int = 30,
            wait_for_completion: bool = False,
    ) -> str:
        """remove assets from a set either by query or by ids."""
        if not set_id and not self.set_id:
            no_set_provided_error()

        set_id = set_id or self.set_id
        if not set_id:
            raise ValueError("No default set available")

        if query is None and ids is None:
            raise ValueError(
                "Either a search query or a list of ids must be provided")

        if self.set_is_locked(set_id):
            if wait_for_availability:
                t_start = time.time()
                while True:
                    time.sleep(1)
                    if time.time() - t_start > timeout:
                        raise TimeoutError(
                            "Timeout waiting for set {} to unlock".format(set_id))
                    if not self.set_is_locked(set_id):
                        logger.info(
                            "Set {} is locked, waiting 1s to remove assets".format(set_id))
                        break
            else:
                raise SetsError("Set {} is locked".format(set_id))

        if query:
            resp = self.requests.post(
                "sets/{}/remove_assets_query/".format(set_id),
                trailing_slash=True,
                json=query)
        else:
            assets_payload = {"asset_list": ids}
            resp = self.requests.post(
                "sets/{}/remove_assets_list/".format(set_id),
                trailing_slash=True,
                json=assets_payload)

        if not resp.ok:
            raise ResponseError(
                "Could not remove assets from set: {}, {}".format(
                    resp.content, resp.reason))

        if wait_for_completion:
            job_id = resp.json()["job_id"]
            self._wait_for_job_completion(job_id)

        return resp.json().get("job_id")

    def assets_in_set(self, set_id: Optional[str] = None) -> List[str]:
        """List assets within a set."""
        return self.search_within_set(set_id=set_id, show_meta=False)

    def search_within_set(
            self,
            query: Optional[dict] = None,
            set_id: Optional[str] = None,
            show_meta: bool = True) -> List:
        """Search for assets within a set."""
        query = query or {}
        if not set_id and not self.set_id:
            no_set_provided_error()

        set_id = set_id or self.set_id
        if show_meta:
            resp = self.requests.post(
                "sets/{}/list_assets_meta/".format(set_id),
                trailing_slash=True,
                json=query)
        else:
            resp = self.requests.post(
                "sets/{}/list_assets/".format(set_id),
                trailing_slash=True,
                json=query)

        if not resp.ok:
            raise ResponseError(
                "Could not perform the search: {}".format(
                    resp.content))

        return resp.json()["results"]

    def search_over_sets(self, query=None, show_meta=True):
        """Search over available sets with a query."""
        query = query or {}
        if show_meta:
            return self.get_asset_manager_client(
                asset_type=AssetsConstants.SETS_ASSET_ID).search_meta(query)
        else:
            return self.get_asset_manager_client(
                asset_type=AssetsConstants.SETS_ASSET_ID).search_assets(query)

    def zip_set(self, set_id: Optional[str] = None) -> (str, str):
        """Create a zipfile of the set."""
        if not set_id and not self.set_id:
            no_set_provided_error()
        set_id = set_id or self.set_id
        resp = self.requests.get(
            "sets/{}/zip_all_assets/".format(set_id),
            trailing_slash=True)
        resp.raise_for_status()
        return resp.json().get("job_id"), resp.json().get("zip_id")

    def download_zipfile(self,
                         zip_id: str,
                         output_filename: Optional[str] = None) -> Union[str,
                                                                         io.BytesIO]:
        """Download a zipfile into either a bytesIO object or a file."""
        data_bytes = self.get_asset_manager_client(
            asset_type=AssetsConstants.ZIPFILES_ASSET_ID).get_bytes(
            id=zip_id)
        if output_filename:
            if not output_filename.endswith(".zip"):
                output_filename += ".zip"
            fpath = join(self.artifacts_path, output_filename)
            with open(fpath, "wb") as f:
                f.write(data_bytes)
            return fpath
        else:
            bytes_file = io.BytesIO(data_bytes)
            return bytes_file

    def download_timeseries(self,
                            search_dic: Optional[Dict] = None,
                            fields: Optional[List[str]] = None) -> dict:
        """Download the timeseries using a search query"""
        timeseries_data = defaultdict(list)
        json_payload = search_dic or {}
        resp = self.requests.post(
            "session_manager/search/",
            json=json_payload,
            trailing_slash=True)

        if not resp.ok:
            raise ResponseError(
                "{} ::: {} with token::: {}".format(
                    resp.reason, resp.content, self.auth_token))
        if fields and TIMESTAMP_FIELD not in fields:
            fields.append(TIMESTAMP_FIELD)
        session_interval_map = resp.json()
        for session_uid, v in session_interval_map.items():
            session_timeseries_data = {}
            intervals = v.get("intervals", [])
            for interval in intervals:
                session_timeseries_data["start_time"] = interval[0]
                session_timeseries_data["end_time"] = interval[1]
                search_dic["time_range"] = {
                    "start_time": interval[0],
                    "end_time": interval[1]
                }
                field_data = self.get_field_data(session_uid=session_uid,
                                                 search_dic=search_dic,
                                                 fields=fields)

                for field, data in field_data.items():
                    if field != TIME_INDEX_FIELD:
                        session_timeseries_data[field] = data
                timeseries_data[session_uid].append(session_timeseries_data)
        return dict(timeseries_data)

    def zip_set_and_download(self,
                             set_id: Optional[str] = None,
                             filename: Optional[str] = None) -> Union[str,
                                                                      io.BytesIO]:
        job_id, zip_id = self.zip_set(set_id)
        self._wait_for_job_completion(job_id)
        return self.download_zipfile(zip_id, output_filename=filename)

    def with_asset_state(
            self,
            asset_type: str,
            metadata_only: bool = False
    ) -> AssetManagerClient:
        """Set the asset state, for use in chaining.

        Eg. client.with_asset_state("images", True).search_files({})
        """
        return self.get_asset_manager_client(asset_type=asset_type)

    def register_rosbag_session(
            self,
            session_name: str,
            session_directory_path: Optional[str] = None,
            rosbag_ids: Optional[List[str]] = None,
            config_name: Optional[str] = None,
            wait_for_completion: bool = True,
    ) -> Tuple[str, str]:
        """Register a rosbag session with the scene engine.

        Args:
            session_name (str): Name of the session
            session_directory_path (str): Local path (on ros-extractor) to a session directory
            rosbag_ids (list): List of rosbag IDs belonging to the session
            config_name (str): Name of the session configuration file
            wait_for_completion: should we wait till completion
        """
        if session_directory_path is None and rosbag_ids is None:
            # Insufficient arguments provided
            raise ValueError(
                "Must provide either session_directory_path or rosbag_ids")

        json_payload = {
            'session_name': session_name,
            'session_directory_path': session_directory_path,
            'source_data': rosbag_ids,
            'session_configuration': config_name,
        }

        resp = self.requests.post(
            "indexing/register_rosbag_session/",
            trailing_slash=True,
            json=json_payload)

        job_id = resp.json()["job_id"]

        if wait_for_completion:
            self._wait_for_job_completion(job_id)

        session_uid = resp.json()["session_uid"]

        return job_id, session_uid

    def get_session_resolution_status(self, session_uid: str) -> str:
        """Get the status of the session resolution task (if it exists)"""
        resp = self.requests.get(
            "session_manager/resolution_status/{}".format(session_uid),
            trailing_slash=False
        )
        return resp.json()['status']

    def submit_rosbag_indexing_request(
            self,
            session_uid: str,
            session_directory_path: Optional[str] = None,
            rosbag_ids: Optional[List[str]] = None,
            config_name: Optional[str] = None,
            extraction_sensors: Optional[List[dict]] = None,
            extraction_types: Optional[List[dict]] = None,
            extraction_settings: Optional[dict] = None,
            enrichments: Optional[List[dict]] = None,
            re_resolve: bool = False,
            wait_for_completion: bool = True
    ) -> str:
        """Submit indexing requests to the scene-engine.

        Args:
            session_uid (str): UID of the session
            session_directory_path (str): Local path (on ros-extractor) to a session directory
            rosbag_ids (list): List of rosbag IDs belonging to the session
            config_name (str): Name of the session configuration file
            extraction_sensors (dict): List of sensor extractions of form:
                {
                    "sensor_name": <sensor name>,
                    "extraction_settings": <dict of extraction settings>,
                    "extraction_types": <list of applicable extraction types>
                }
            extraction_types (list): List of type extractions of form:
                {
                    "extraction_type": <Type of extraction>,
                    "extraction_settings": <Extraction settings for this type>
                }
            extraction_settings (dict): Fallback extraction settings
            wait_for_completion: should we wait till completion
        """
        if session_directory_path is None and rosbag_ids is None:
            # Insufficient arguments provided
            raise ValueError(
                "Must provide either session_directory_path or rosbag_ids")

        if extraction_types is None and extraction_sensors is None:
            raise ValueError(
                "Must provide one of extraction_types or extraction_sensors")

        json_payload = {
            'session_uid': session_uid,
            'session_directory_path': session_directory_path,
            'source_data': rosbag_ids,
            'session_configuration': config_name,
            'extraction_config': {
                'extraction_sensors': extraction_sensors or [],
                'extraction_types': extraction_types or [],
                'extraction_settings': extraction_settings or {},
            },
            'enrichments': enrichments or [],
            're_resolve': re_resolve
        }

        return self.requests.post(
            "indexing/index_rosbag_session/",
            trailing_slash=True,
            json=json_payload)

    def submit_video_indexing_request(
            self,
            session_name: str,
            video_session_data: Optional[dict] = None,
            video_filenames: Optional[List[str]] = None,
            raw_videos: Optional[dict] = None,
            session_formatting_strategy: Optional[str] = None,
            extraction_config: Optional[dict] = None,
            wait_for_completion: bool = True,
            retry: Optional[bool] = False,
            enrichments: Optional[List[dict]] = None,
            session_uid: Optional[str] = None

    ) -> dict:

        resp = self.requests.post(
            "indexing/index_video_session/",
            trailing_slash=True,
            json={
                'session_name': session_name,
                'video_session_data': video_session_data or [],
                'raw_videos': raw_videos or {},
                'extraction_config': extraction_config or {},
                'video_filenames': video_filenames,
                'session_formatting_strategy': session_formatting_strategy,
                'retry': retry,
                'enrichments': enrichments,
                'session_uid': session_uid,
            }
        )

        if not resp.ok:
            raise IndexingException(
                "Failed to index video session: {} -- {}".format(resp.reason, resp.content))

        if wait_for_completion:
            job_ids = [resp.json()["job_id"]]
            successful_jobs = 0
            failed_jobs = 0

            t1 = time.time()
            job_info = wait_for_jobs(
                job_ids=job_ids,
                asset_manager_url=self.asset_manager_url,
                auth_token=self.auth_token,
                timeout=None,
                raise_on_error=True)
            logger.info(
                "JOBS finished in {} seconds".format(
                    round(time.time() - t1), 2))
            successful_jobs += job_info['successful']
            failed_jobs += job_info['failed']

        return resp.json()

    def extract_video_images_and_compress(
            self, video_id: str, session_name: str):
        resp = self.requests.post(
            'videos/extract_and_compress_video/',
            json={
                'video_id': video_id,
                'session_name': session_name
            },
            trailing_slash=True
        )
        return resp.json()

    def submit_hls_indexing_request(
            self,
            session_name: str,
            session_directory_path: Optional[str] = None,
            hls_ids: Optional[List[str]] = None,
            config_name: Optional[str] = None,
            extraction_sensors: Optional[List[dict]] = None,
            extraction_types: Optional[List[dict]] = None,
            extraction_settings: Optional[dict] = None,
    ):
        # TODO have a separate client for HLS related methods
        """Submit indexing requests to the scene-engine.

        Args:
            session_name (str): Name of the session
            session_directory_path (str): Local path to a session directory
            hls_ids (list): List of hls IDs belonging to the session
            config_name (str): Name of the session configuration file
            extraction_sensors (dict): List of sensor extractions of form:
                {
                    "sensor_name": <sensor name>,
                    "extraction_settings": <dict of extraction settings>,
                    "extraction_types": <list of applicable extraction types>
                }
            extraction_types (list): List of type extractions of form:
                {
                    "extraction_type": <Type of extraction>,
                    "extraction_settings": <Extraction settings for this type>
                }
            extraction_settings (dict): Fallback extraction settings
        """

        if session_directory_path is None and hls_ids is None:
            # Insufficient arguments provided
            raise ValueError(
                "Must provide either session_directory_path or hls_ids")

        if extraction_types is None and extraction_sensors is None:
            raise ValueError(
                "Must provide one of extraction_types or extraction_sensors")

        json_payload = {
            'session_name': session_name,
            'session_directory_path': session_directory_path,
            'source_data': hls_ids,
            'session_configuration': config_name,
            'extraction_config': {
                'extraction_sensors': extraction_sensors or [],
                'extraction_types': extraction_types or [],
                'extraction_settings': extraction_settings or {},
            }
        }

        resp = self.requests.post(
            "indexing/index_hls_session/",
            trailing_slash=True,
            json=json_payload)
        return resp.json()

    def get_indexing_job_components(self, indexing_job_task_id):
        resp = self.requests.get(
            "indexing/job_components/{}".format(indexing_job_task_id),
            trailing_slash=False
        )
        return resp.json()

    def get_annotation_project_assets(self, annotation_project_id):
        annotation_project_state = self.get_asset_manager_client(
            asset_type=AssetsConstants.ANNOTATION_PROJECTS_ASSET_ID).get_metadata(annotation_project_id)["state"]
        annotation_project_files = []
        for set_id, set_files in json.loads(annotation_project_state).items():
            annotation_project_files.extend(set_files)
        return annotation_project_files

    def get_asset_annotation_files(self, assets_list):
        # TODO: It's not currently possible to have more than on annotation for the same asset, and needs to be fixed
        # TODO: Handle cases other than images
        annotation_filenames = [i.replace(".png", ".ann") for i in assets_list]
        return annotation_filenames

    def get_searchable_field_statistics(self, asset_type: str) -> dict:
        return self.requests.get(
            route=os.path.join(
                asset_type,
                'meta',
                'searchable_field_statistics'),
            trailing_slash=True).json()

    def get_metadata(
            self,
            id: str,
            asset_type: str,
            with_session_metadata: bool = False) -> dict:
        if with_session_metadata is False:
            return self.get_asset_manager_client(
                asset_type=asset_type).get_metadata(id)
        else:
            resp = self.requests.get(
                route=os.path.join(
                    asset_type,
                    'meta',
                    id),
                trailing_slash=False,
                params={'with_session_metadata': True}
            )
            if not resp.ok:
                raise ResponseError(
                    "{} ::: {} with token::: {}".format(
                        resp.reason, resp.content, self.auth_token))
            return resp.json()

    def compress_images(self,
                        ids: List[str],
                        desired_shape: Optional[Tuple[int,
                                                      ...]] = None,
                        thumbnail_tag: Optional[str] = None,
                        use_preset: Optional[str] = None):
        resp = self.requests.post(
            "images/compress_images/",
            trailing_slash=True,
            json={
                "ids": ids,
                "desired_shape": desired_shape,  # h x w x ..
                "thumbnail_tag": thumbnail_tag,
                "use_preset": use_preset,
            }
        )

        return resp.json()

    def compress_videos(self,
                        ids: List[str],
                        desired_shape: Optional[Tuple[int,
                                                      ...]] = None,
                        thumbnail_tag: Optional[str] = None,
                        use_preset: Optional[str] = None,
                        job_id: Optional[str] = None
                        ):
        resp = self.requests.post(
            "videos/compress_videos/",
            trailing_slash=True,
            json={
                "ids": ids,
                "desired_shape": desired_shape,  # h x w x ..
                "thumbnail_tag": thumbnail_tag,
                "use_preset": use_preset,
                "job_id": job_id
            }
        )

        return resp.json()

    def compress_lidars(self,
                        ids: List[str],
                        skip_factors: Optional[List[int]] = None
                        ):
        skip_factors = skip_factors or [1, 10, 100]
        resp = self.requests.post(
            "lidars/compress_lidars/",
            trailing_slash=True,
            json={
                "ids": ids,
                "skip_factors": skip_factors
            }
        )

        return resp.json()

    def concatenate_videos(
            self,
            ids: List[str],
            output_video_id: str,
            video_metadata: dict,
            job_id: Optional[str] = None):
        resp = self.requests.post(
            "videos/concatenate_videos/",
            trailing_slash=True,
            json={
                "ids": ids,
                "output_video_id": output_video_id,
                "video_metadata": video_metadata,
                "job_id": job_id
            }
        )

        return resp.json()

    def add_annotation(self,
                       annotation: Annotation,
                       raw_annotation: Optional[str] = None,
                       update_asset: bool = True,
                       buffered_write: bool = False):

        metadata = annotation.to_dic()

        self.get_asset_manager_client(
            asset_type=AssetsConstants.ANNOTATIONS_ASSET_ID).put_asset(
            metadata=metadata,
            id=annotation.id,
            file_object=raw_annotation,
            wait_for_completion=buffered_write
        )

        if update_asset:
            self.get_asset_manager_client(
                asset_type=annotation.media_type).update_metadata(
                id=annotation.asset_id,
                metadata={
                    "annotations": [
                        annotation.id],
                    "annotations_meta": [{
                        "provider": annotation.provider,
                        "id": annotation.id,
                        "type": annotation.annotation_type}]})

    def add_annotations(self,
                        annotations: Iterable[Annotation],
                        buffered_write: bool = True,
                        update_asset: bool = True,
                        threading: bool = True
                        ):

        run_threaded(func=self.add_annotation,
                     iterable=annotations,
                     desc="adding annotations",
                     buffered_write=buffered_write,
                     update_asset=update_asset,
                     disable_threading=not threading)

    def compare_annotation_pairs(self,
                                 asset_id: str,
                                 asset_type: str,
                                 base_annotation_id: Optional[str] = None,
                                 other_annotation_id: Optional[str] = None,
                                 base_mapping: Optional[str] = None,
                                 other_mapping: Optional[str] = None,
                                 iou_threshold: Optional[float] = None,
                                 match_labels: Optional[bool] = None,
                                 wait_for_completion: Optional[bool] = False):
        json_resquest = {
            "asset_id": asset_id,
            "asset_type": asset_type
        }
        if base_annotation_id:
            json_resquest.update(
                {
                    "base_annotation_id": base_annotation_id,
                }
            )
        if other_annotation_id:
            json_resquest.update(
                {
                    "other_annotation_id": other_annotation_id,
                }
            )
        if base_mapping:
            json_resquest.update(
                {
                    "base_mapping": base_mapping,
                }
            )
        if other_mapping:
            json_resquest.update(
                {
                    "other_mapping": other_mapping,
                }
            )
        if iou_threshold:
            json_resquest.update(
                {
                    "iou_threshold": iou_threshold,
                }
            )
        if match_labels is not None:
            json_resquest.update(
                {
                    "match_labels": match_labels,
                }
            )
        resp = self.requests.post(
            "annotations_comparisons/compare_annotation_pairs/",
            trailing_slash=True,
            json=json_resquest
        )

        if wait_for_completion:
            job_id = resp.json()["job_id"]
            self._wait_for_job_completion(job_id)
        return resp.json()

    def get_standardized_session_name(self, session_name: str):
        resp = self.requests.post(
            "sessions/standardize_name/",
            trailing_slash=True,
            json={
                'session_name': session_name})

        if not resp.ok:
            raise ResponseError("{} ::: {}".format(resp.reason, resp.content))
        return resp.json()['session_name']

    def get_indexed_session_filenames(self, search_query):
        # Get all the indexed sessions
        indexed_sessions = self.get_asset_manager_client(
            AssetsConstants.SESSIONS_ASSET_ID).search_assets(search_query)
        return indexed_sessions

    def _get_asset_response_model(self, asset_type: str):
        if asset_type not in AssetsConstants.VALID_ASSETS:
            raise ValueError("Invalid asset type {}".format(asset_type))
        return self.requests.get(
            route=os.path.join(asset_type, 'meta', 'response_model'),
            trailing_slash=True
        ).json()

    def add_session(self,
                    session_name: str,
                    session_type: str = SessionTypes.GENERIC_SESSION_ID,
                    resolution: Optional[float] = None) -> str:
        payload = {
            "session_name": session_name,
            "session_type": session_type
        }
        if resolution:
            payload["resolution"] = resolution
        resp = self.requests.post(
            "sessions/add/",
            trailing_slash=True,
            json=payload)
        if not resp.ok:
            raise ResponseError("{} ::: {}".format(resp.reason, resp.content))
        return resp.json().get("session_uid")

    def update_time_span(
            self,
            session_uid: str,
            session_start_time: Union[datetime, str],
            session_end_time: Union[datetime, str]) -> dict:
        logger.info(
            "session_start_time {} and session_end_time {}".format(
                session_start_time,
                session_end_time))
        resp = self.requests.post(
            "sessions/update_time_span/",
            trailing_slash=True,
            json={
                "session_uid": session_uid,
                "session_start_time": datetime_or_str_to_iso_utc(session_start_time),
                "session_end_time": datetime_or_str_to_iso_utc(session_end_time)})
        if not resp.ok:
            raise ResponseError("{} ::: {}".format(resp.reason, resp.content))
        return resp.json()

    def add_source_data(
            self,
            session_uid: str,
            source_data: List[dict],
            sensors: List[dict],
            replace: Optional[bool] = True) -> dict:
        resp = self.requests.post(
            "sessions/add_source_data/",
            trailing_slash=True,
            json={
                "session_uid": session_uid,
                "source_data": source_data,
                "sensors": sensors,
                "replace": replace})
        if not resp.ok:
            raise ResponseError("{} ::: {}".format(resp.reason, resp.content))
        return resp.json()

    def add_auxiliary_session_data(
            self,
            session_uid: str,
            auxiliary_data: List[dict],
            replace: Optional[bool] = True) -> dict:
        resp = self.requests.post(
            "sessions/add_auxiliary_data/",
            trailing_slash=True,
            json={
                "session_uid": session_uid,
                "auxiliary_data": auxiliary_data,
                "replace": replace})
        if not resp.ok:
            raise ResponseError("{} ::: {}".format(resp.reason, resp.content))
        return resp.json()

    def add_enrichments_configs(
            self,
            session_uid: str,
            enrichments_configs: List[dict],
            replace: Optional[bool] = True) -> dict:
        resp = self.requests.post(
            "sessions/add_enrichments_configs/",
            trailing_slash=True,
            json={
                "session_uid": session_uid,
                "enrichments_configs": enrichments_configs,
                "replace": replace})
        if not resp.ok:
            raise ResponseError("{} ::: {}".format(resp.reason, resp.content))
        return resp.json()

    def add_geolocation_entity(
            self,
            geolocation: dict,
            entity_value: List[str],
            timestamp: int,
            session_uid: str):

        entity_dict = {
            "session": session_uid,
            "timestamp": datetime_or_str_to_iso_utc(timestamp),
            "enrichments": ["visibility", "weather", "city", "country"],
            "entity_id": get_guid(),
            "geolocation": geolocation,
            "entity_name": EntityNames.GEOLOCATION,
            "entity_value": entity_value,
            "entity_type": EntityTypes.GEO_ENTITY_TYPE,
            "influence": EntityInfluenceTypes.GEO_INTERPOLATION
        }
        entity_id = self.add_entity(
            entity_dict=entity_dict)
        return entity_id

    def add_entity(self,
                   entity_dict: dict,
                   urgent: bool = False) -> dict:
        # urgent messages are ingested immediately but a manual resolution is
        # needed after that to make them searchable
        if not entity_dict.get("session"):
            raise InvalidArgumentsError(
                "session is not specified"
            )
        resp = self.requests.post(
            "session_manager/add_entity/",
            trailing_slash=True,
            json={"entity_dict": entity_dict},
            params={"urgent": urgent}
        )
        if not resp.ok:
            raise ResponseError("{} ::: {}".format(resp.reason, resp.content))
        return resp.json()

    def add_entities(self,
                     entity_dicts: List[dict]) -> dict:

        resp = self.requests.post(
            "session_manager/add_entities/",
            trailing_slash=True,
            json={"entity_dicts": entity_dicts},
        )
        if not resp.ok:
            raise ResponseError("{} ::: {}".format(resp.reason, resp.content))
        return resp.json()

    def resolve_session(
            self,
            session_uid: str,
            resolution: Optional[float] = None,
            wait_for_completion: bool = False) -> dict:
        if resolution:
            params = {"resolution": resolution}
        else:
            params = {}
        resp = self.requests.post(
            "session_manager/resolve_session/{}".format(session_uid),
            params=params)
        if not resp.ok:
            raise ResponseError("{} ::: {}".format(resp.reason, resp.content))
        if wait_for_completion:
            job_id = resp.json()["job_id"]
            self._wait_for_job_completion(job_id)
        return resp.json()

    def add_event_interval(self,
                           event_name: str,
                           event_value: Union[str, List[str]],
                           start_time: Union[str, datetime],
                           end_time: Union[str, datetime],
                           session_uid: str,
                           urgent: bool = False
                           ) -> str:
        if isinstance(start_time, datetime) and isinstance(end_time, datetime):
            if start_time > end_time:
                raise InvalidTimeError(
                    "start time cannot be after the end time")
        entity_id = get_guid()
        if isinstance(event_value, str):
            event_value = [event_value]
        elif not isinstance(event_value, list):
            raise TypeError("event value can be either str or a List[str]")
        entity_dict = {
            "session": session_uid,
            "start_time": datetime_or_str_to_iso_utc(start_time),
            "end_time": datetime_or_str_to_iso_utc(end_time),
            "timestamp": datetime_or_str_to_iso_utc(start_time),
            "entity_id": entity_id,
            "entity_name": event_name,
            "entity_value": event_value,
            "entity_type": EntityTypes.STATE_SET_ENTITY_TYPE,
            "influence": EntityInfluenceTypes.AFFECT_FORWARD
        }

        self.add_entity(entity_dict=entity_dict, urgent=urgent)
        # self.resolve_session(session_uid=session_uid)

        return entity_id

    def add_comments(self,
                     comments: Union[str, List[str]],
                     start_time: Union[str, datetime],
                     end_time: Union[str, datetime],
                     session_uid: str,
                     wait_for_completion: bool = False) -> str:

        if isinstance(comments, str):
            comments = [comments]

        comment_json = {
            "intervals": [
                {
                    "start_time": datetime_or_str_to_iso_utc(start_time),
                    "end_time": datetime_or_str_to_iso_utc(end_time)
                }
            ],
            "texts": comments,
        }
        resp = self.requests.post(
            "sessions/{}/comments".format(session_uid),
            trailing_slash=False,
            json=comment_json
        )
        if wait_for_completion:
            job_id = resp.json()["job_id"]
            self._wait_for_job_completion(job_id)
        return resp.json()

    def get_field_data(self,
                       session_uid: str,
                       search_dic: dict = None,
                       fields: Union[List[str],
                                     str] = 'all') -> Dict[str,
                                                           list]:
        if not search_dic:
            search_dic = {}

        if isinstance(fields, str):
            if fields == 'all':
                fields = ['*']
            else:
                raise ValueError(
                    'Field {} is not valid. Must be a list of field names or `all`'.format(fields))

        resp = self.requests.post(
            "session_manager/field_data/{}".format(session_uid),
            trailing_slash=False,
            json={
                'search_dic': search_dic,
                'session_fields': fields
            }
        )
        return resp.json()

    def get_searchable_fields(self, asset_type: str) -> dict:
        return self.requests.get(
            route=os.path.join(
                asset_type,
                'meta',
                'search_fields'),
            trailing_slash=True).json()

    def __adjust_time_interval(self,
                               start_time: Union[datetime, str],
                               end_time: Union[datetime, str],
                               epsilon: float) -> (datetime, datetime):

        if isinstance(start_time, str):
            start_time_output = string_to_datetime(
                start_time) + timedelta(seconds=epsilon)
        elif isinstance(start_time, datetime):
            start_time_output = start_time + timedelta(seconds=epsilon)
        else:
            raise TypeError("time should be either datetime or string")

        if isinstance(end_time, str):
            end_time_output = string_to_datetime(
                end_time) - timedelta(seconds=epsilon)
        elif isinstance(end_time, datetime):
            end_time_output = end_time - timedelta(seconds=epsilon)
        else:
            raise TypeError("time should be either datetime or string")

        if start_time_output > end_time_output:
            raise InvalidTimeError(
                "start time cannot be after or within {} second of the end time".format(epsilon))
        return start_time_output, end_time_output

    def add_event_intervals(self,
                            event_name: str,
                            event_values: List[str],
                            start_times: List[Union[str, datetime]],
                            end_times: List[Union[str, datetime]],
                            session_uid: str,
                            epsilon: float = 0) -> List[str]:

        if len(event_values) != len(start_times) or \
                len(event_values) != len(end_times):
            raise IndexError(
                "size of event_values, start_times, and end_times should be same")

        entity_ids = []
        for start_time, end_time, event_value in zip(
                start_times, end_times, event_values):
            start_time, end_time = self.__adjust_time_interval(
                start_time, end_time, epsilon)

            entity_id = get_guid()
            if not isinstance(event_value, str):
                raise TypeError("event value should be str")

            entity_dict = {
                "session": session_uid,
                "start_time": datetime_or_str_to_iso_utc(start_time),
                "end_time": datetime_or_str_to_iso_utc(end_time),
                "timestamp": datetime_or_str_to_iso_utc(start_time),
                "enrichments": [],
                "entity_id": entity_id,
                "entity_name": event_name,
                "entity_value": [event_value],
                "entity_type": EntityTypes.STATE_SET_ENTITY_TYPE,
                "influence": EntityInfluenceTypes.AFFECT_FORWARD
            }

            self.add_entity(entity_dict=entity_dict)
            entity_ids.append(entity_id)

        # self.resolve_session(session_uid=session_uid)

        return entity_ids

    def add_scalar_intervals(self,
                             measurement_name: str,
                             measurement_values: List[float],
                             start_times: List[Union[str, datetime]],
                             end_times: List[Union[str, datetime]],
                             session_uid: str,
                             epsilon: float = 0.001) -> List[str]:

        if len(measurement_values) != len(start_times) or \
                len(measurement_values) != len(end_times):
            raise IndexError(
                "size of event_values, start_times, and end_times should be same")

        timestamps = []
        unpacked_measurements = []

        for start_time, end_time, measurement_value in zip(
                start_times, end_times, measurement_values):

            start_time, end_time = self.__adjust_time_interval(
                start_time, end_time, epsilon)

            timestamps += [start_time, end_time]
            unpacked_measurements += [measurement_value, measurement_value]

        return self.add_scalar_measurements(
            measurement_name=measurement_name,
            measurement_values=unpacked_measurements,
            timestamps=timestamps,
            session_uid=session_uid)

    def add_scalar_measurements(self,
                                measurement_name: str,
                                measurement_values: List[float],
                                timestamps: List[Union[datetime, str]],
                                session_uid: str) -> List[str]:

        entity_ids = []
        entity_dicts = []
        if len(timestamps) != len(measurement_values):
            raise IndexError(
                "measurement_values and timestamps should have same length")

        for timestamp, measurement_value in zip(
                timestamps, measurement_values):

            entity_id = get_guid()
            entity_dict = {
                "session": session_uid,
                "timestamp": datetime_or_str_to_iso_utc(timestamp),
                "enrichments": [],
                "entity_id": entity_id,
                "entity_name": measurement_name,
                "entity_value": measurement_value,
                "entity_type": EntityTypes.SCALAR_ENTITY_TYPE,
                "influence": EntityInfluenceTypes.LINEAR_INTERPOLATION
            }
            entity_dicts.append(entity_dict)
            entity_ids.append(entity_id)

        self.add_entities(entity_dicts=entity_dicts)
        return entity_ids

    def add_point_events(self,
                         measurement_name: str,
                         measurement_values: List[str],
                         timestamps: List[Union[datetime, str]],
                         session_uid: str) -> List[str]:

        if len(timestamps) != len(measurement_values):
            raise IndexError(
                "measurement_values and timestamps should have same length")

        entity_ids = []
        entity_dicts = []
        resolution = self.with_asset_state(
                            AssetsConstants.SESSIONS_ASSET_ID).get_metadata(
                            id=session_uid).get("resolution")
        for timestamp, measurement_value in zip(
                timestamps, measurement_values):

            entity_id = get_guid()
            timestamp = str_or_datetime_to_datetime(timestamp)
            start_time = datetime_or_str_to_iso_utc(timestamp - timedelta(seconds=resolution))
            end_time = datetime_or_str_to_iso_utc(timestamp + timedelta(seconds=resolution))
            timestamp = datetime_or_str_to_iso_utc(timestamp)
            entity_dict = {
                "session": session_uid,
                "timestamp": timestamp,
                "start_time": start_time,
                "end_time": end_time,
                "enrichments": [],
                "entity_id": entity_id,
                "entity_name": measurement_name,
                "entity_value": measurement_value,
                "entity_type": EntityTypes.STATE_ENTITY_TYPE,
                "influence": EntityInfluenceTypes.INTERVAL
            }
            entity_dicts.append(entity_dict)
            entity_ids.append(entity_id)

        self.add_entities(entity_dicts=entity_dicts)

    def add_timeseries_csv(self,
                session_uid: str,
                csv_filepath: str,
                ):
        measurement_df = pd.read_csv(csv_filepath)

        self.add_df(
            measurement_df=measurement_df,
            session_uid=session_uid
        )

    def add_df(self,
                      measurement_df: pd.DataFrame,
                      session_uid: str,
                      timestamps: Optional[List[Union[datetime,
                                                      str]]] = None):

        def add_numeric_df(column: str,
                                  measurement_df: pd.DataFrame,
                                  timestamps: List[datetime]):

            measurement_values = [
                float(x) for x in measurement_df[column].values]
            self.add_scalar_measurements(
                measurement_name=column.lower(),
                measurement_values=measurement_values,
                timestamps=timestamps,
                session_uid=session_uid)

        if TIMESTAMP_FIELD not in measurement_df.columns and not timestamps:
            raise KeyError(
                "dataframe must include a timestamp column or timestamps must be passed separately")
        if not timestamps:
            timestamps = [str_or_datetime_to_datetime(
                _) for _ in measurement_df.timestamp]
        numeric_df = measurement_df.select_dtypes(include=np.number)
        non_numeric_df = measurement_df.drop(labels=numeric_df.columns, axis=1)
        non_numeric_df.drop(labels=TIMESTAMP_FIELD, axis=1, inplace=True)

        if not numeric_df.empty:
            run_threaded(func=add_numeric_df,
                         iterable=numeric_df.columns,
                         desc="adding scalar measurements",
                         measurement_df=numeric_df,
                         timestamps=timestamps)
        if not non_numeric_df.empty:
            for column in non_numeric_df.columns:
                self.add_point_events(
                    measurement_name=column,
                    measurement_values=non_numeric_df[column],
                    session_uid=session_uid,
                    timestamps=timestamps)
        self.resolve_session(session_uid=session_uid)

    def delete_session(self,
                       session_uid: str,
                       delete_assets_contents: bool = True,
                       wait_for_completion: bool = False):
        resp = self.requests.delete(
            "session_manager/delete_session/{}".format(session_uid),
            trailing_slash=False,
            params={'delete_assets_contents': delete_assets_contents})
        if not resp.ok:
            raise ResponseError("{} ::: {}".format(resp.reason, resp.content))

        if wait_for_completion:
            job_id = resp.json()["job_id"]
            self._wait_for_job_completion(job_id)
        return resp.json()

    def add_event_with_search(self,
                              event_title: str,
                              search: dict,
                              wait_for_completion: bool = False):

        resp = self.requests.post("session_manager/add_event_with_search/",
                                  trailing_slash=False,
                                  json={
                                      "search": search,
                                      "event_title": event_title}
                                  )
        if not resp.ok:
            raise ResponseError("{} ::: {}".format(resp.reason, resp.content))

        if wait_for_completion:
            job_id = resp.json()["job_id"]
            self._wait_for_job_completion(job_id)
        return resp.json()

    def delete_events(self,
                      session_uids: List[str],
                      event_names: List[str],
                      start_time: Optional[str] = None,
                      end_time: Optional[str] = None,
                      wait_for_completion: bool = False):
        params = {'session_uids': session_uids,
                  'event_names': event_names}
        if start_time:
            params["start_time"] = start_time
        if end_time:
            params["end_time"] = end_time

        resp = self.requests.delete(
            "session_manager/delete_event/",
            trailing_slash=False,
            json=params)
        if not resp.ok:
            raise ResponseError("{} ::: {}".format(resp.reason, resp.content))

        if wait_for_completion:
            job_id = resp.json()["job_id"]
            self._wait_for_job_completion(job_id)
        return resp.json()

    def search_assets(
            self,
            asset_type,
            query: Optional[dict] = None,
            size: int = DEFAULT_SEARCH_SIZE,
            offset: int = 0,
            sort_field: Optional[str] = None,
            sort_order: Optional[str] = None,
            scan: bool = False) -> List[str]:

        query = query or {}
        params = {'size': size, 'offset': offset, 'scan': scan}
        if sort_field:
            params['sort_field'] = sort_field
        if sort_order:
            params['sort_order'] = sort_order

        resp = self.requests.post("{}/".format(asset_type),
                                  json=query,
                                  params=params,
                                  trailing_slash=False)
        if not resp.ok:
            raise AssetError(
                'Could not search the files ::: {} -- {} -- {}'.format(
                    asset_type, resp.reason, resp.content))
        return resp.json()

    def search_meta(
            self,
            asset_type,
            query: Optional[dict] = None,
            size: int = DEFAULT_SEARCH_SIZE,
            offset: int = 0,
            sort_field: Optional[str] = None,
            sort_order: Optional[str] = None,
            scan: bool = False) -> List[Dict]:

        query = query or {}
        params = {'size': size, 'offset': offset, 'scan': scan}
        if sort_field:
            params['sort_field'] = sort_field
        if sort_order:
            params['sort_order'] = sort_order

        resp = self.requests.post("{}/meta/".format(asset_type),
                                  json=query,
                                  params=params,
                                  trailing_slash=False)
        if not resp.ok:
            raise AssetError(
                'Could not search the files ::: {} -- {} -- {}'.format(
                    asset_type, resp.reason, resp.content))
        return resp.json()

    def add_embeddings(
            self,
            media_asset_id_embedding_bytes_map: Dict,
            asset_type: str,
            ndim: int,
            model: str,
            version: str,
            layer: Optional[str] = None,
            set_id: Optional[str] = None,
            similarity_ingest: bool = True,
            wait_for_completion: bool = False,
            buffered_write: bool = False,
            threading: bool = True,
    ) -> List[str]:

        embedding_ids = []

        def add_embedding_threaded(iterable):
            media_asset_id, embedding_bytes = iterable
            timestamp = datetime.utcnow()
            json_object_for_embedding_id = {
                'model': model,
                'version': version,
                'asset_id': media_asset_id,
                'layer': layer,
                'ndim': ndim}

            embeddings_hash = get_md5_from_json_object(json_object=json_object_for_embedding_id)
            embedding_id = str(hash_string_into_positive_integer_reproducible(embeddings_hash))

            embedding_meta = {
                'id': embedding_id,
                'timestamp': timestamp,
                'ndim': ndim,
                'sets': [set_id] if set_id else [],
                'tags': [layer] if layer else [],
                'media_type': asset_type,
                'asset_id': media_asset_id,
                'model': model,
                'version': version,
                'index_name': get_similarity_index_name(
                    media_type=asset_type,
                    model=model,
                    version=version)}

            self.get_asset_manager_client(
                AssetsConstants.EMBEDDINGS_ASSET_ID).put_asset(
                file_object=embedding_bytes,
                id=embedding_id,
                metadata=embedding_meta,
                buffered_write=buffered_write,
                retry=True)

            similarity_index_name = get_similarity_index_name(
                media_type=asset_type, model=model, version=version)

            self.get_asset_manager_client(
                asset_type=asset_type).update_metadata(
                id=media_asset_id, metadata={
                    "embeddings": {similarity_index_name: embedding_id}},
                    retry=True)
            embedding_ids.append(embedding_id)

        run_threaded(func=add_embedding_threaded,
                     iterable=media_asset_id_embedding_bytes_map.items(),
                     desc="adding embeddings",
                     disable_threading=not threading)

        if similarity_ingest:

            resp = self.requests.post(
                "similarity_search/bulk_index/",
                trailing_slash=False,
                json={"embedding_ids": embedding_ids})
            if not resp.ok:
                raise ResponseError(
                    "Could not clean_up the annotations: {}".format(
                        resp.content))

            job_id = resp.json()["job_id"]
            if wait_for_completion:
                self._wait_for_job_completion(
                    job_id, max_wait_sec=max(
                        10 * len(embedding_ids), 60))

        return embedding_ids

    def add_image(
            self,
            image_path: Optional[str] = None,
            image_url: Optional[str] = None,
            image_uri: Optional[str] = None,
            image_bytes: Optional[Union[io.BytesIO, bytes, str]] = None,
            sensor: Optional[str] = None,
            timestamp: Optional[Union[str, datetime]] = None,
            session_uid: Optional[str] = None,
            id: Optional[str] = None,
            set_id: Optional[str] = None,
            annotations: Optional[List[Annotation]] = None,
            preprocesses: Optional[List[str]] = None,
            aux_metadata: Optional[dict] = None,
            geo_field: Optional[str] = None,
            enrichments: Optional[List[str]] = None,
            thumbnailize_at_ingest: bool = False,
            buffered_write: bool = False,
            add_to_session: bool = False,
            overwrite: bool = True) -> str:

        if not overwrite and id is not None:
            if self.get_asset_manager_client(
                    asset_type=AssetsConstants.IMAGES_ASSET_ID).exists(
                    id=id):
                if aux_metadata or preprocesses or set_id or annotations:
                    updated_meta = {}
                    if set_id:
                        updated_meta['sets'] = [set_id]
                    if aux_metadata:
                        updated_meta[AUXILIARY_KEY] = aux_metadata
                    if preprocesses:
                        updated_meta['preprocesses'] = preprocesses
                    if annotations:
                        updated_meta["annotations"] = [
                            _.id for _ in annotations
                        ]
                        updated_meta["annotations_meta"] = [
                            {
                                "provider": _.provider,
                                "id": _.id,
                                "version": _.version,
                                "type": _.annotation_type
                            } for _ in annotations]
                        for annotation in annotations:
                            image_meta = self.get_asset_manager_client(
                                asset_type=AssetsConstants.IMAGES_ASSET_ID).get_metadata(id=id)
                            annotation.timestamp = image_meta["timestamp"]
                            annotation.sensor = image_meta["sensor"]
                            annotation.session_uid = image_meta["session_uid"]
                        self.add_annotations(
                            annotations=annotations, update_asset=False)

                    self.get_asset_manager_client(
                        asset_type=AssetsConstants.IMAGES_ASSET_ID).update_metadata(
                        id=id, metadata=updated_meta)
                return id

        if sum(1 for _ in [image_path, image_url, image_uri, image_bytes] if _ is not None) != 1:
            raise InvalidArgumentsError(
                "Exactly one of image_path, image_url, image_uri, and image_bytes should be specified")

        if image_bytes:
            image_attributes = get_image_attributes(image_bytes=image_bytes)
            filename = id
        elif image_path:
            filename, _, _, image_format = parse_file_path(image_path)
            image_attributes = get_image_attributes(image_path=image_path)
            with open(image_path, 'rb') as f:
                image_bytes = io.BytesIO(f.read())
        elif image_url:
            filename = image_url.split("/")[-1]
            image_attributes = get_image_attributes(image_url=image_url)
        elif image_uri:
            filename = UriParser(uri=image_uri).key.split("/")[-1]
            object_access = ObjectAccess(
                uri=image_uri
            )
            image_attributes = get_image_attributes(
                self.get_asset_manager_client(
                    AssetsConstants.IMAGES_ASSET_ID).get_url_from_object_access(
                    object_access=object_access))
        else:
            raise ValueError(
                "Either image file path, image bytes, or url must be provided")

        if timestamp is None:
            timestamp = datetime.utcnow()
        else:
            timestamp = datetime_or_str_to_iso_utc(timestamp)

        image_metadata = {
            "session_uid": session_uid,
            "width": image_attributes.width,
            "height": image_attributes.height,
            "format": image_attributes.format,
            "sensor": sensor,
            "timestamp": timestamp,
            "sets": [set_id] if set_id else [],
            "preprocesses": preprocesses or [],
        }

        if annotations:
            image_metadata["annotations"] = [
                _.id for _ in annotations
            ]
            image_metadata["annotations_meta"] = [
                {
                    "provider": _.provider,
                    "id": _.id,
                    "version": _.version,
                    "type": _.annotation_type
                } for _ in annotations]
            labels = set()
            for annotation in annotations:
                for ae in annotation.annotation_entities:
                    labels.add(ae.label)

            labels = list(labels)

            if aux_metadata:
                aux_metadata["labels"] = labels
            else:
                aux_metadata = {"labels": labels}

        if aux_metadata:
            image_metadata[AUXILIARY_KEY] = aux_metadata
        if image_bytes:
            id = self.get_asset_manager_client(
                AssetsConstants.IMAGES_ASSET_ID).put_asset(
                file_object=image_bytes,
                filename=filename,
                id=id,
                metadata=image_metadata,
                geo_field=geo_field,
                wait_for_completion=not buffered_write,
                buffered_write=buffered_write,
            )
        else:
            id = self.get_asset_manager_client(
                AssetsConstants.IMAGES_ASSET_ID).put_asset(
                url=image_url,
                filename=filename,
                id=id,
                uri=image_uri,
                metadata=image_metadata,
                geo_field=geo_field,
                wait_for_completion=not buffered_write,
                buffered_write=buffered_write
            )

        # If session_uid does not exist skip creating and pushing the entity
        if session_uid and add_to_session:
            entity_dict = {
                "session": session_uid,
                "timestamp": timestamp,
                "enrichments": enrichments or [],
                "entity_name": EntityNames.IMAGE,
                "media_asset_id": id,
                "entity_value": id,
                "entity_type": EntityTypes.MEDIA,
                "influence": EntityInfluenceTypes.INTERVAL
            }
            self.add_entity(entity_dict=entity_dict)

        # create thumbnail at ingestion time. By default set to False to speed up ingestion. If false, it thumbnails
        # will be created on the fly
        if thumbnailize_at_ingest:

            for preset in ["small", "tiny", "full_size_png"]:
                self.compress_images(
                    ids=[id],
                    use_preset=preset
                )

        if annotations:
            for annotation in annotations:
                annotation.timestamp = timestamp
                annotation.sensor = sensor
                annotation.session_uid = session_uid

            self.add_annotations(annotations=annotations, update_asset=False, threading=False)
        return id

    def add_video(
            self,
            video_path: Optional[str] = None,
            video_url: Optional[str] = None,
            video_uri: Optional[str] = None,
            sensor: Optional[str] = None,
            start_timestamp: Optional[Union[datetime, str]] = None,
            session_uid: Optional[str] = None,
            id: Optional[str] = None,
            set_id: Optional[str] = None,
            enrichments: Optional[List[str]] = None,
            tags: Optional[List[str]] = None,
            compress_video: bool = True,
            buffered_write: bool = False,
            add_to_session: bool = False) -> str:

        id = id or get_guid()
        if video_path:
            filename, _, _, _ = parse_file_path(video_path)
            video_attributes = get_video_attributes(video_path)
        elif video_url:
            filename = video_url.split("/")[-1]
            video_attributes = get_video_attributes(video_url)
        elif video_uri:
            filename = UriParser(uri=video_uri).key.split("/")[-1]
            object_access = ObjectAccess(
                uri=video_uri
            )
            video_attributes = get_video_attributes(
                self.get_asset_manager_client(
                    AssetsConstants.VIDEOS_ASSET_ID).get_url_from_object_access(
                    object_access=object_access))
        else:
            raise ValueError("Either file path or url must be provided")

        if start_timestamp:
            start_timestamp_dt = str_or_datetime_to_datetime(start_timestamp)
        else:
            start_timestamp_dt = datetime.utcnow()

        video_metadata = {
            "timestamp": datetime_or_str_to_iso_utc(start_timestamp_dt),
            "width": video_attributes.width,
            "height": video_attributes.height,
            "sensor": sensor,
            "duration": float(video_attributes.duration),
            "fps": video_attributes.fps,
            "session_uid": session_uid,
            "sets": [set_id] if set_id else [],
            "start_time": datetime_or_str_to_iso_utc(start_timestamp_dt),
            "end_time": datetime_or_str_to_iso_utc(
                start_timestamp_dt
                + timedelta(
                    seconds=float(video_attributes.duration))),
            "tags": tags or []
        }
        if video_path:
            id = self.get_asset_manager_client(
                AssetsConstants.VIDEOS_ASSET_ID).put_asset(
                file_path=video_path,
                filename=filename,
                metadata=video_metadata,
                id=id,
                wait_for_completion=not buffered_write,
                buffered_write=buffered_write
            )
        elif video_url or video_uri:
            id = self.get_asset_manager_client(
                AssetsConstants.VIDEOS_ASSET_ID).put_asset(
                url=video_url,
                uri=video_uri,
                metadata=video_metadata,
                id=id,
                wait_for_completion=not buffered_write,
                buffered_write=buffered_write
            )
        else:
            raise ValueError(
                "Either file path or url, or uri must be provided ")

        # If session_uid does not exist skip creating and pushing the entity
        if session_uid and add_to_session:
            entity_dict = {
                "session": video_metadata["session_uid"],
                "start_time": video_metadata["start_time"],
                "end_time": video_metadata["end_time"],
                "timestamp": video_metadata["timestamp"],
                "enrichments": enrichments or [],
                "entity_name": EntityNames.VIDEO,
                "entity_type": EntityTypes.MEDIA,
                "entity_value": id,
                "media_asset_id": id,
                "influence": EntityInfluenceTypes.AFFECT_FORWARD
            }
            self.add_entity(entity_dict=entity_dict)
        if compress_video:
            for preset in ['small', 'tiny']:
                self.compress_videos(
                    ids=[id],
                    use_preset=preset,
                )
        return id

    def add_lidar(
            self,
            lidar_path: Optional[str] = None,
            lidar_url: Optional[str] = None,
            lidar_uri: Optional[str] = None,
            sensor: Optional[str] = None,
            timestamp: Optional[Union[str, datetime]] = None,
            session_uid: Optional[str] = None,
            id: Optional[str] = None,
            format: Optional[str] = None,
            set_id: Optional[str] = None,
            enrichments: Optional[List[str]] = None,
            buffered_write: bool = False,
            add_to_session: bool = False) -> str:

        if lidar_path:
            filename, _, _, image_format = parse_file_path(lidar_path)
        elif lidar_url:
            filename = lidar_url.split("/")[-1]
        elif lidar_uri:
            filename = UriParser(uri=lidar_uri).key.split("/")[-1]
        else:
            raise ValueError("Either file path or url must be provided")

        if timestamp is None:
            timestamp = datetime.utcnow()
        else:
            timestamp = datetime_or_str_to_iso_utc(timestamp)

        lidar_metadata = {"session_uid": session_uid,
                          "format": format,
                          "sensor": sensor,
                          "timestamp": timestamp,
                          "sets": [set_id] if set_id else []}

        if lidar_path:
            id = self.get_asset_manager_client(
                AssetsConstants.LIDARS_ASSET_ID).put_asset(
                file_path=lidar_path,
                filename=filename,
                metadata=lidar_metadata,
                id=id,
                wait_for_completion=not buffered_write,
                buffered_write=buffered_write
            )
        elif lidar_url or lidar_uri:
            id = self.get_asset_manager_client(
                AssetsConstants.LIDARS_ASSET_ID).put_asset(
                url=lidar_url,
                uri=lidar_uri,
                metadata=lidar_metadata,
                id=id,
                wait_for_completion=not buffered_write,
                buffered_write=buffered_write
            )
        else:
            raise ValueError(
                "Either file path or url, or uri must be provided ")

        # If session_uid does not exist skip creating and pushing the entity
        if session_uid and add_to_session:
            entity_dict = {
                "session": session_uid,
                "timestamp": timestamp,
                "enrichments": enrichments or [],
                "entity_name": EntityNames.LIDAR,
                "media_asset_id": id,
                "entity_value": id,
                "entity_type": EntityTypes.MEDIA,
                "influence": EntityInfluenceTypes.INTERVAL
            }
            self.add_entity(entity_dict=entity_dict)

        self.compress_lidars(
            ids=[id],
            skip_factors=[1, 10, 100]
        )
        return id

    def cleanup_annotation_masks(self,
                                 ids: Optional[List[str]] = None,
                                 search: Optional[dict] = None,
                                 wait_for_completion: bool = True) -> str:
        payload = {}
        if ids is not None:
            payload["ids"] = ids
        if search is not None:
            payload["search"] = search

        resp = self.requests.post(
            "annotations/cleanup_annotation_masks/",
            trailing_slash=False,
            json=payload)
        if not resp.ok:
            raise ResponseError(
                "Could not clean_up the annotations: {}".format(
                    resp.content))

        job_id = resp.json()["job_id"]
        if wait_for_completion:
            self._wait_for_job_completion(
                job_id, max_wait_sec=max(
                    10 * len(ids), 60))
        return job_id

    def annotations_to_objects(self,
                               ids: Optional[List[str]] = None,
                               search: Optional[dict] = None,
                               create_objects: bool = False,
                               margin_ratio: float = 0.1,
                               wait_for_completion: bool = True) -> str:

        payload = {'create_objects': create_objects,
                   'margin_ratio': margin_ratio
                   }
        if ids is not None:
            payload["ids"] = ids
        if search is not None:
            payload["search"] = search

        resp = self.requests.post(
            "annotations/annotations_to_objects/",
            trailing_slash=False,
            json=payload)
        if not resp.ok:
            raise ResponseError(
                "Could not create objects from annotations: {}".format(
                    resp.content))

        job_id = resp.json()["job_id"]
        if wait_for_completion:
            self._wait_for_job_completion(job_id, max_wait_sec=2 * len(ids))
        return job_id

    def compress_masks_batch(
            self,
            thumbnail_tag: str,
            ids: Optional[List[str]] = None,
            search: Optional[dict] = None,
            wait_for_completion: bool = True) -> str:

        payload = {}
        if ids is not None:
            payload["ids"] = ids
        if search is not None:
            payload["search"] = search

        payload["thumbnail_tag"] = thumbnail_tag

        resp = self.requests.post(
            "annotations/compress_masks_batch/",
            trailing_slash=False,
            json=payload)
        if not resp.ok:
            raise ResponseError(
                "Could not create objects from annotations: {}".format(
                    resp.content))

        job_id = resp.json()["job_id"]
        if wait_for_completion:
            self._wait_for_job_completion(job_id)
        return job_id

    def mrcnn_inference(self,
                        ids: Optional[List[str]] = None,
                        search: Optional[dict] = None,
                        obtain_mask: bool = True,
                        obtain_bbox: bool = True,
                        obtain_object_entities: bool = True,
                        obtain_embeddings: bool = True,
                        threshold: Optional[float] = None,
                        classes_of_interest: Optional[List[str]] = None,
                        wait_for_completion: bool = False
                        ):

        payload = {
            "obtain_mask": obtain_mask,
            "obtain_bbox": obtain_bbox,
            "obtain_object_entities": obtain_object_entities,
            "obtain_embeddings": obtain_embeddings,
            "ids": ids or []
        }
        if threshold is not None:
            payload["threshold"] = threshold

        if classes_of_interest is not None:
            payload["classes_of_interest"] = classes_of_interest

        if search is not None:
            payload["search"] = search

        resp = self.requests.post(
            "images/mrcnn_inference/",
            trailing_slash=False,
            json=payload)

        job_id = resp.json()["job_id"]
        if wait_for_completion:
            self._wait_for_job_completion(job_id)
        return job_id

    def add_object_embeddings(self,
                              ids: Optional[List[str]] = None,
                              search: Optional[dict] = None,
                              wait_for_completion: bool = True):
        payload = {
            "ids": ids or []
        }
        if search is not None:
            payload["search"] = search

        resp = self.requests.post(
            "objects/add_object_embeddings/",
            trailing_slash=False,
            json=payload)
        if not resp.ok:
            raise ResponseError(
                "Could not fetch embeddings for objects: {}".format(
                    resp.content))

        job_id = resp.json()["job_id"]
        if wait_for_completion:
            self._wait_for_job_completion(job_id)
        return job_id

    def submit_enricher(self,
                        enricher_class: Type[Enricher]) -> str:
        if not issubclass(enricher_class, Enricher):
            raise AssetError("Problem with Enricher class")

        metadata = {
            "version": enricher_class.version,
            "type": "udf",
            TIMESTAMP_FIELD: datetime.utcnow()
        }

        return self.get_asset_manager_client(
            asset_type=AssetsConstants.UDFS_ASSET_ID).put_asset(
            metadata=metadata, file_object=pickle.dumps(enricher_class))

    def enricher_dry_run(self,
                         enricher_class: Type[Enricher],
                         metadata: dict
                         ):

        enricher_id = self.submit_enricher(enricher_class=enricher_class)

        payload = {
            "enricher_ids": [enricher_id],
            "metadata": metadata
        }

        resp = self.requests.post(
            "enrichers/dry_run/",
            trailing_slash=False,
            json=payload)

        return resp.json()

    def enricher_batch(
            self,
            enricher_class: Type[Enricher],
            assets_type: str,
            ids: Optional[List[str]] = None,
            search: Optional[dict] = None,
            wait_for_completion: bool = False
    ) -> str:

        payload = {
            "ids": ids or []
        }

        if search is not None:
            payload["search"] = search

        enricher_id = self.submit_enricher(enricher_class=enricher_class)

        payload["enricher_ids"] = [enricher_id]
        payload["assets_type"] = assets_type

        resp = self.requests.post(
            "enrichers/batch/",
            trailing_slash=False,
            json=payload)

        job_id = resp.json()["job_id"]
        if wait_for_completion:
            self._wait_for_job_completion(job_id)
        return job_id

    def extract_images_from_videos(
        self,
        video_id: str,
        extract_start_time: Optional[Union[datetime, str]] = None,
        extract_end_time: Optional[Union[datetime, str]] = None,
        fps: Optional[float] = None,
        set_id: Optional[id] = None,
        wait_for_completion: bool = False
    ) -> str:

        payload = {
            "id": video_id
        }
        if extract_start_time:
            payload["extract_start_time"] = datetime_or_str_to_iso_utc(
                extract_start_time)

        if extract_end_time:
            payload["extract_end_time"] = datetime_or_str_to_iso_utc(
                extract_end_time)

        if fps:
            payload["fps"] = fps

        if set_id:
            payload["set_id"] = set_id

        resp = self.requests.post(
            "videos/extract_images/",
            trailing_slash=False,
            json=payload)

        job_id = resp.json()["job_id"]
        if wait_for_completion:
            self._wait_for_job_completion(job_id)
        return job_id

    def images_to_video(self,
                        session_uid: str,
                        sensor: str,
                        fps: Optional[int] = None,
                        search: Optional[dict] = None,
                        image_format: Optional[str] = None,
                        video_id: Optional[str] = None,
                        wait_for_completion: bool = False) -> str:

        payload = {
            "id": video_id,
            "sensor": sensor,
            "search": search,
            "image_format": image_format,
            "session_uid": session_uid,
            "video_id": video_id or get_guid(),
            "fps": fps
        }
        resp = self.requests.post(
            "videos/images_to_video/",
            trailing_slash=False,
            json=payload)
        job_id = resp.json()["job_id"]
        if wait_for_completion:
            self._wait_for_job_completion(job_id)
        return job_id

    def similarity_search_bulk_index(
            self,
            embedding_ids: Optional[List[str]] = None,
            search_dic: Optional[dict] = None,
            wait_for_completion: bool = False):

        payload = {}
        if embedding_ids is not None:
            payload["embedding_ids"] = embedding_ids
        if search_dic is not None:
            payload["search_dic"] = search_dic

        logger.debug("Bulk index payload: {}".format(payload))

        resp = self.requests.post(
            "similarity_search/bulk_index/",
            trailing_slash=False,
            json=payload)

        job_id = resp.json()["job_id"]
        if wait_for_completion:
            self._wait_for_job_completion(job_id)

        return job_id

    def create_umap(
            self,
            search_dic: Optional[dict] = None,
            n_neighbors: int = 20,
            min_dist: float = 0.3,
            wait_for_completion: bool = False):

        payload = {
            "search": search_dic or {},
            "n_neighbors": n_neighbors,
            "min_dist": min_dist
        }

        logger.debug("create_umap payload: {}".format(payload))

        resp = self.requests.post(
            "embeddings/create_umap/",
            trailing_slash=False,
            json=payload)

        job_id = resp.json()["job_id"]
        if wait_for_completion:
            self._wait_for_job_completion(job_id)

        return job_id

    def display_url(self,
                    url: str):
        try:
            full_url = "{}{}".format(self.front_end_url, url)
            display(Javascript('window.open("{url}");'.format(url=full_url)))
        except NameError:
            logger.error("Cannot display in this environment- Please use Colab or Jupyter")

    def display_image(self, image_id: str):
        self.display_url(url="images?image={}".format(image_id))

    def display_video(self, video_id: str):
        self.display_url(url="videos?video={}".format(video_id))

    def display_object(self, object_id: str):
        self.display_url(url="objects?object={}".format(object_id))

    def display_lidar(self, lidar_id: str):
        self.display_url(url="lidars?lidar={}".format(lidar_id))

    def display_session(self, session_uid: str):
        self.display_url(url="sessions?session_uid={}".format(session_uid))

    def display_set(self, set_id: str):
        self.display_url(url="sets?set={}".format(set_id))

    def display_projects(self, project_id: str):
        self.display_url(url="projects?project={}".format(project_id))


class SceneEngineRequestHandler:
    """Helper for making authenticated requests to the scene engine."""

    def __init__(
            self,
            scene_engine_url,
            auth_token=None):
        self.scene_engine_url = scene_engine_url
        self.auth_token = auth_token

    def with_auth(self,
                  auth_token: Optional[str] = None,
                  ):
        if auth_token:
            self.auth_token = auth_token

        return self

    def get(self,
            route,
            trailing_slash=False,
            params=None,
            headers=None,
            remove_version=False):
        return self.__make_scene_engine_request(
            method="get",
            route=route,
            trailing_slash=trailing_slash,
            params=params,
            headers=headers,
            remove_version=remove_version)

    def post(
            self,
            route,
            trailing_slash=False,
            params=None,
            json=None,
            headers=None,
            remove_version=False):
        return self.__make_scene_engine_request(
            method="post",
            route=route,
            trailing_slash=trailing_slash,
            params=params,
            json=json,
            headers=headers,
            remove_version=remove_version)

    def put(
            self,
            route,
            trailing_slash=False,
            params=None,
            json=None,
            headers=None,
            remove_version=False):
        return self.__make_scene_engine_request(
            method="put",
            route=route,
            trailing_slash=trailing_slash,
            params=params,
            json=json,
            headers=headers,
            remove_version=remove_version)

    def delete(
            self,
            route,
            trailing_slash=False,
            params=None,
            json=None,
            headers=None,
            remove_version=False):
        return self.__make_scene_engine_request(
            method="delete",
            route=route,
            trailing_slash=trailing_slash,
            params=params,
            json=json,
            headers=headers,
            remove_version=remove_version)

    def __make_scene_engine_request(
            self,
            method: str,
            route: str = "",
            trailing_slash: bool = False,
            params: Optional[dict] = None,
            json: Optional[dict] = None,
            headers: Optional[dict] = None,
            remove_version: bool = False):
        assert method in {"get", "post", "put", "delete"}
        url = self.__get_scene_engine_url(
            route, trailing_slash, remove_version)
        request_ = getattr(requests, method)
        if self.auth_token:
            if not params:
                params = {}
            params["token"] = self.auth_token
        resp = request_(
            url,
            params=params,
            json=json,
            headers=headers)
        if not resp.ok:
            raise ResponseError(
                "{} ::: {} with token::: {}".format(
                    resp.reason, resp.content, self.auth_token))
        return resp

    def __get_scene_engine_url(self, route, trailing_slash, remove_version):

        if remove_version:
            scene_engine_url_ = re.sub(
                "{}".format(VERSION_POSTFIX), "", self.scene_engine_url)
        else:
            scene_engine_url_ = self.scene_engine_url

        url = join(scene_engine_url_, route)
        if trailing_slash and not url.endswith("/"):
            url += "/"
        return url
