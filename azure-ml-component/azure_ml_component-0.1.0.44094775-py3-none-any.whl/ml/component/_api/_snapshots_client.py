# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
import os
import json
from functools import reduce
from uuid import UUID

from azureml._common.async_utils import TaskQueue
from azureml._common.exceptions import AzureMLException
from azureml._file_utils import upload_blob_from_stream
from azureml.exceptions import SnapshotException, UserErrorException
from azureml._base_sdk_common.snapshot_dto import SnapshotDto
from azureml._base_sdk_common.merkle_tree_differ import compute_diff
from azureml._base_sdk_common.tracking import global_tracking_info_registry
from azureml._base_sdk_common.common import get_http_exception_response_string
from azureml._base_sdk_common.merkle_tree import DirTreeJsonEncoder, create_merkletree, DirTreeNode

from azure.ml.component._util._loggerfactory import track, _LoggerFactory
from azure.ml.component._util._telemetry import WorkspaceTelemetryMixin
from azure.ml.component._api._utils import create_session_with_retry
from azure.ml.component._util._utils import TimerContext
from ._utils import _EMPTY_GUID
from ._snapshot_cache import SnapshotCache
from ._snapshots_client_core import (
    SnapshotsClient as BaseSnapshotsClient,
    MAX_FILES_SNAPSHOT_UPLOAD_PARALLEL,
    AZUREML_SNAPSHOT_DEFAULT_TIMEOUT,
    TIMEOUT,
    RETRY_LIMIT,
    BACKOFF_START,
    DirTreeJsonEncoderV2
)
from .._aml_core_dependencies import SNAPSHOT_MAX_FILES, ONE_MB

SNAPSHOT_MAX_SIZE_BYTES = 2 * 1024 * ONE_MB
_logger = None


def _get_logger():
    global _logger
    if _logger is not None:
        return _logger
    _logger = _LoggerFactory.get_logger(__name__)
    return _logger


class SnapshotsClient(BaseSnapshotsClient, WorkspaceTelemetryMixin):
    """
    Snapshot client class, extended from azureml._restclient.snapshots_client.SnapshotsClient.
    Add snapshot cache per component.

    :param workspace: Workspace for this client
    :type workspace: azureml.core.Workspace
    :param logger: the logger used to log info and warning happened during uploading snapshot
    :type logger: logging.Logger
    """

    def __init__(self, workspace, logger=None):
        # the mro of this class is BaseSnapshotsClient -> WorkspaceClient -> ClientBase -> ChainedIdentity
        # -> WorkspaceTelemetryMixin -> TelemetryMixin -> object
        super(SnapshotsClient, self).__init__(workspace.service_context, workspace=workspace)
        self._cache = SnapshotCache(self._service_context)
        if not logger:
            self.logger = logging.getLogger('snapshot')
        else:
            self.logger = logger

    def validate_snapshot_size(self, size, component_file, raise_on_validation_failure):
        """Validate size of snapshot.

        :param size: Size of component snapshot.
        :param component_file: The component spec file.
        :param raise_on_validation_failure: Raise error if validation failed.
        """
        if size > SNAPSHOT_MAX_SIZE_BYTES and not os.environ.get("AML_SNAPSHOT_NO_FILE_SIZE_LIMIT"):
            error_message = "====================================================================\n" \
                            "\n" \
                            "While attempting to take snapshot of {}\n" \
                            "Your total snapshot size exceeds the limit of {} MB.\n" \
                            "You can overwrite the size limit by specifying environment variable " \
                            "AML_SNAPSHOT_NO_FILE_SIZE_LIMIT, for example in bash: " \
                            "export AML_SNAPSHOT_NO_FILE_SIZE_LIMIT=True. \n" \
                            "Please see http://aka.ms/troubleshooting-code-snapshot on how to debug " \
                            "the creating process of component snapshots.\n" \
                            "\n" \
                            "====================================================================\n" \
                            "\n".format(component_file, SNAPSHOT_MAX_SIZE_BYTES / ONE_MB)
            if raise_on_validation_failure:
                raise SnapshotException(error_message)
            else:
                self.logger.warning(error_message)

    def _validate_snapshot_file_count(self, file_or_folder_path, file_number, raise_on_validation_failure):
        if file_number > SNAPSHOT_MAX_FILES and not os.environ.get("AML_SNAPSHOT_NO_FILE_LIMIT"):
            error_message = "====================================================================\n" \
                            "\n" \
                            "While attempting to take snapshot of {}\n" \
                            "Your project exceeds the file limit of {}.\n" \
                            "Please see http://aka.ms/troubleshooting-code-snapshot on how to debug " \
                            "the creating process of component snapshots.\n" \
                            "\n" \
                            "====================================================================\n" \
                            "\n".format(file_or_folder_path, SNAPSHOT_MAX_FILES)
            if raise_on_validation_failure:
                raise SnapshotException(error_message)
            else:
                self.logger.warning(error_message)

    @track(_get_logger)
    def create_snapshot(
            self, snapshot_folder, size,
            component_file=None, retry_on_failure=True, raise_on_validation_failure=True):
        """Create snapshot on given merkle tree root and snapshot size.
        support cache and incrementally update based on latest snapshot

        :param component_file: Component base folder, used to calculate cache file location
        :param snapshot_folder: Snapshot base folder.
        :param size: snapshot size
        :param retry_on_failure:
        :param raise_on_validation_failure:
        :return:
        """
        if component_file is None:
            component_file = snapshot_folder

        # add extra dimensions(eg: snapshot size, upload time) to logger
        track_dimensions = {}

        self.validate_snapshot_size(size, component_file, raise_on_validation_failure)

        # Get the previous snapshot for this project
        try:
            parent_root, parent_snapshot_id = self._cache.get_latest_snapshot_by_path(component_file)
        except json.decoder.JSONDecodeError:
            # Removing the cache file if found corrupted
            self._cache.remove_cache(component_file)
            parent_root, parent_snapshot_id = self._cache.get_latest_snapshot_by_path(component_file)

        # Compute the dir tree for the current working set
        # The folder passed here has already excluded ignored files, so we do not need to check that
        def _is_file_excluded(file):
            return False

        curr_root = create_merkletree(snapshot_folder, _is_file_excluded)

        # Compute the diff between the two dirTrees
        entries = compute_diff(parent_root, curr_root)
        dir_tree_file_contents = json.dumps(curr_root, cls=DirTreeJsonEncoder)

        # If there are no changes, just return the previous snapshot_id
        if not len(entries):
            self.logger.info("The snapshot did not change compared to local cached one, reused local cached snapshot.")
            track_dimensions.update({'local_cache': True})
            _LoggerFactory.add_track_dimensions(_get_logger(), track_dimensions)
            return parent_snapshot_id

        # get new snapshot id by snapshot hash
        snapshot_id = str(UUID(curr_root.hash[::4]))
        track_dimensions.update({'snapshot_id': snapshot_id})

        # Check whether the snapshot with new id already exists
        with TimerContext() as timer_context:
            snapshot_dto = self.get_snapshot_metadata_by_id(snapshot_id)
            get_snapshot_metadata_duration_seconds = timer_context.get_duration_seconds()
            track_dimensions.update({'get_snapshot_metadata_duration_seconds': get_snapshot_metadata_duration_seconds})

        if snapshot_dto is None:
            entries_to_send = [entry for entry in entries if (
                entry.operation_type == 'added' or entry.operation_type == 'modified') and entry.is_file]
            self._validate_snapshot_file_count(component_file, len(entries_to_send), raise_on_validation_failure)

            # Git metadata
            snapshot_properties = global_tracking_info_registry.gather_all(snapshot_folder)

            headers = {'Content-Type': 'application/json; charset=UTF-8'}
            headers.update(self.auth.get_authentication_header())

            with create_session_with_retry() as session:
                self.logger.info(
                    "Uploading snapshot files, only added or modified files will be uploaded.")
                with TimerContext() as timer_context:

                    try:
                        revision_list = self._upload_snapshot_files(
                            entries_to_send, snapshot_folder, _is_file_excluded)
                    except AzureMLException as e:
                        # when uploading snapshot fails, record snapshot info from upload request
                        total_size = 0
                        try:
                            for entry in entries_to_send:
                                if hasattr(entry, 'node_path'):
                                    total_size += os.path.getsize(os.path.join(snapshot_folder, entry.node_path))
                        except BaseException:
                            pass
                        track_dimensions.update({
                            'files_to_send': len(entries_to_send),
                            'total_size': total_size
                        })
                        # log files to send and total size here so we can have that when uploading failed
                        _LoggerFactory.add_track_dimensions(_get_logger(), track_dimensions)
                        raise e
                    else:
                        # otherwise, record snapshot file info from upload result
                        total_size = reduce((lambda s, x: s + x['FileSize']), revision_list, 0)
                        total_size = total_size / 1024
                        track_dimensions.update({
                            'files_to_send': len(revision_list),
                            'total_size': total_size
                        })
                        _LoggerFactory.add_track_dimensions(_get_logger(), track_dimensions)

                    # only log uploaded files when snapshot cache exists
                    if parent_snapshot_id != _EMPTY_GUID:
                        for entry in entries_to_send:
                            self.logger.info("\t{} {}".format(
                                str(entry.operation_type).capitalize(), entry.node_path))

                    collect_duration_seconds = timer_context.get_duration_seconds()
                    track_dimensions.update({
                        'upload_duration_seconds': collect_duration_seconds
                    })
                    self.logger.info(
                        'Uploaded {} files in {:.2f} seconds, total size {:.2f} KB'.format(
                            len(revision_list), collect_duration_seconds, total_size))

                create_data = {"ParentSnapshotId": parent_snapshot_id, "Tags": None, "Properties": snapshot_properties}
                create_data.update({"DirTreeNode": curr_root})
                create_data.update({"FileRevisionList": {"FileNodes": revision_list}})

                data = json.dumps(create_data, cls=DirTreeJsonEncoderV2)
                encoded_data = data.encode('utf-8')

                url = self._service_context._get_project_content_url() + "/content/v2.0" + \
                    self._service_context._get_workspace_scope() + "/snapshots/" + snapshot_id

                # record time spent when uploading snapshot
                with TimerContext() as timer_context:
                    response = self._execute_with_base_arguments(
                        session.post, url, data=encoded_data, headers=headers)
                    upload_duration_seconds = timer_context.get_duration_seconds()
                    track_dimensions.update({
                        'create_duration_seconds': upload_duration_seconds
                    })
                    self.logger.info('Created snapshot in {:.2f} seconds.'.format(upload_duration_seconds))

                if response.status_code >= 400:
                    if retry_on_failure:
                        # The cache may have been corrupted, so clear it and try again.
                        self._cache.remove_latest()
                        return self.create_snapshot(
                            snapshot_folder, size, component_file, retry_on_failure=False)
                    else:
                        raise SnapshotException(get_http_exception_response_string(response))

            snapshot_dto = SnapshotDto(dir_tree_file_contents, snapshot_id)
        else:
            self.logger.info("Found remote cache of snapshot, reused remote cached snapshot.")
            track_dimensions.update({'workspace_cache': True})

        # Update the cache
        self._cache.update_cache(snapshot_dto, component_file)
        # update tracked dimensions
        _LoggerFactory.add_track_dimensions(_get_logger(), track_dimensions)
        return snapshot_id

    def get_snapshot_metadata_by_id(self, snapshot_id):
        """
        200 indicates the snapshot with this id exists, 404 indicates not exists
        If other status codes returned, by default we will retry 3 times until we get 200 or 404
        """
        auth_headers = self.auth.get_authentication_header()
        url = self._service_context._get_project_content_url() + "/content/v1.0" + \
            self._service_context._get_workspace_scope() + "/snapshots/" + \
            snapshot_id + "/metadata"
        with create_session_with_retry() as session:
            response = self._execute_with_base_arguments(
                session.get, url, headers=auth_headers)
            if response.status_code == 200:
                response_data = response.content.decode('utf-8')
                snapshot_dict = json.loads(response_data)
                root_dict = snapshot_dict['root']
                snapshot_id = snapshot_dict['id']
                node = DirTreeNode()
                node.load_object_from_dict(root_dict)
                root = json.dumps(node, cls=DirTreeJsonEncoder)
                return SnapshotDto(root, snapshot_id)
            elif response.status_code == 404:
                return None
            else:
                raise SnapshotException(get_http_exception_response_string(response))

    def _upload_files_batch(self, file_nodes, file_or_folder_path, session):
        """ Upload files in batch.

        When timeout error happens, throw error with clear message to guide user overwrite it.

        :param file_nodes: File nodes list.
        :param file_or_folder_path: Snapshot file/folder path
        :param session: Request session
        :return: Revision file list with blob URL, eg: [
                {"FullName": file_name1, "BlobUri": upload_url1, "FileSize": file_size1},
                {"FullName": file_name2, "BlobUri": upload_url2, "FileSize": file_size2},
                ...
            ], map from upload tasks to it's results
        """
        batch_size = MAX_FILES_SNAPSHOT_UPLOAD_PARALLEL
        results = []
        revision_list = []
        flush_timeout_seconds = AZUREML_SNAPSHOT_DEFAULT_TIMEOUT
        timeout_env_var = "AZUREML_SNAPSHOT_TIMEOUT_SECONDS"
        # get flush timeout, if user set AZUREML_SNAPSHOT_TIMEOUT_SECONDS in environment var, use it
        if os.environ.get(timeout_env_var):
            try:
                flush_timeout_seconds = float(os.environ.get(timeout_env_var))
            except ValueError:
                raise UserErrorException(
                    "Environment variable {} with value {} set but failed to parse. "
                    "Please reset the value to a number.".format(timeout_env_var, os.environ.get(timeout_env_var)))

        identity = "snapshot_upload_files"
        for i in range(0, len(file_nodes), batch_size):
            with TaskQueue(worker_pool=self._pool, flush_timeout_seconds=flush_timeout_seconds,
                           _ident=identity, _parent_logger=self._logger) as task_queue:
                batch_nodes = file_nodes[i:i + batch_size]

                def perform_upload(file_or_folder_path, file_name, upload_url, session):
                    with open(os.path.join(file_or_folder_path, file_name), "rb") as data:
                        return upload_blob_from_stream(data, upload_url, session=session, timeout=TIMEOUT,
                                                       backoff=BACKOFF_START, retries=RETRY_LIMIT)

                for node in batch_nodes:
                    file_name = node['fullName']
                    upload_url = node['blobUri']
                    task = task_queue.add(perform_upload, file_or_folder_path, file_name, upload_url, session)
                    results.append(task)

                    file_size = os.path.getsize(os.path.join(file_or_folder_path, file_name))
                    file_revision = {"FullName": file_name, "BlobUri": upload_url, "FileSize": file_size}
                    revision_list.append(file_revision)

                try:
                    task_queue.flush(source=identity)
                except AzureMLException as e:
                    # Guide user overwrite AZUREML_SNAPSHOT_DEFAULT_TIMEOUT when timeout happens
                    e.message += (
                        "\nYou can overwrite the flush timeout by specifying corresponding value to "
                        "environment variable {}, "
                        "for example in bash: export {}=900. \n"
                        "Please see http://aka.ms/troubleshooting-code-snapshot on how to debug "
                        "the creating process of component snapshots.".format(timeout_env_var, timeout_env_var)
                    )
                    raise e

        return revision_list, map(lambda task: task.wait(), results)

    def _upload_snapshot_files(self, entries_to_send, file_or_folder_path, exclude_function):
        headers = {'Content-Type': 'application/json; charset=UTF-8'}
        headers.update(self.auth.get_authentication_header())

        file_list = [entry.node_path for entry in entries_to_send]
        file_names = {"FileNames": file_list}

        data = json.dumps(file_names)
        encoded_data = data.encode('utf-8')

        # set pool size to max threads to improve performance
        with create_session_with_retry(pool_maxsize=MAX_FILES_SNAPSHOT_UPLOAD_PARALLEL) as session:
            get_blobs_url = self._service_context._get_project_content_url() + "/content/v2.0" + \
                self._service_context._get_workspace_scope() + "/snapshots/getblob"
            get_blobs_response = self._execute_with_base_arguments(
                session.post, get_blobs_url, data=encoded_data, headers=headers)

            # raise SnapshotException when get blob response fails
            if get_blobs_response.status_code != 200:
                raise SnapshotException(get_http_exception_response_string(get_blobs_response))

            response_data = get_blobs_response.content.decode('utf-8')
            blob_uri_dict = json.loads(response_data)
            try:
                file_nodes = blob_uri_dict['fileNodes']
            except KeyError:
                raise SnapshotException("fileNodes not found in blob response, blob response {}".format(blob_uri_dict))

            revision_list = self._upload_files_batch(file_nodes, file_or_folder_path, session)
            return revision_list[0]
