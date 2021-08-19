# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
import requests
import json
import uuid
from pathlib import Path

from azureml.core import Run as CoreRun
from azureml.core.experiment import Experiment
from azureml._run_impl.run_history_facade import PropertyKeys
from azure.ml.component._api._snapshots_client import SnapshotsClient
from azure.ml.component._util._loggerfactory import _LoggerFactory, track
from .._restclients.designer.models import ErrorResponseException
from ._command_execution_builder import OUTPUT_DIR_NAME
from ._constants import RUN_RELEASE_LOG
from .._util._utils import print_to_terminal


_logger = None


def _get_logger():
    global _logger
    if _logger is not None:
        return _logger
    _logger = _LoggerFactory.get_logger(__name__)
    return _logger


class RunHistoryTracker:
    def __init__(self, run, track_run_history=True, path=None):
        self.run = run
        self.track_run_history = track_run_history
        if path and track_run_history:
            self.create_run_history_log(path)

    @classmethod
    @track(_get_logger)
    def from_run(cls, run, track_run_history, path=None):
        return cls(run, track_run_history, path)

    @classmethod
    @track(_get_logger)
    def with_definition(cls, experiment_name, component, working_dir, track_run_history, path=None):
        """Generate RunHistoryTracker with run definition."""
        run = None
        if track_run_history:
            run = get_current_run()
            if run:
                print_to_terminal(
                    'A run exists in current environment, will use it to create a child run to initialize '
                    'run history tracker of component [ %s ] to record execution information.' %
                    component.name)
                run = run.child_run(name=experiment_name)
            else:
                print_to_terminal(
                    'Start initialize run history tracker of component [ %s ] to record execution information.' %
                    component.name)
                experiment = Experiment(component.workspace, experiment_name)
                run = _get_and_start_run_with_definition(component, experiment, working_dir)
        tracker = cls(run, track_run_history, path)
        print_to_terminal(
            'Finished initialize run history tracker of component [ %s ] to record execution information.' %
            component.name)
        return tracker

    @classmethod
    @track(_get_logger)
    def without_definition(cls, workspace, experiment_name, track_run_history, path=None):
        """Generate RunHistoryTracker without run definition."""
        run = None
        finished_msg = 'Finished initialize run history tracker of experiment [ %s ] to record execution ' \
                       'information.' % experiment_name
        if track_run_history:
            run = get_current_run()
            if run:
                print_to_terminal(
                    'A run exists in current environment, will use it to create a child run to initialize '
                    'run history tracker of pipeline to record execution information.')
                run = run.child_run(name=experiment_name)
                finished_msg = 'Finished initialize run history tracker of pipeline to record execution information.'
            else:
                print_to_terminal(
                    'Start initialize run history tracker of experiment [ %s ] to record execution information.' %
                    experiment_name)
                experiment = Experiment(workspace, experiment_name)
                run = CoreRun._start_logging(experiment, snapshot_directory=None)
        tracker = cls(run, track_run_history, path)
        print_to_terminal(finished_msg)
        return tracker

    @track(_get_logger)
    def update_run_result_status(self, run_success, error_details=None):
        from ..run import Run
        if self.run and not Run._is_terminal_state(self.run):
            if run_success:
                self.run.complete()
            else:
                self.run.fail(error_details=error_details)
            print('Finish uploading run status to run history')

    def get_run(self):
        return self.run

    def get_run_details_url(self):
        if self.run:
            return self.run._run_details_url

    def get_run_id(self):
        if self.run:
            return self.run.id

    def print_run_info(self):
        if self.run:
            print('RunId: %s' % self.run.id)
            print('Link to Azure Machine Learning Portal: %s' % self.run.get_portal_url())

    def add_properties(self, properties):
        """
        Add immutable properties to the run.
        :param properties: The hidden properties stored in the run object.
        :type properties: dict
        """
        if self.run:
            # Avoid modify existing values in Properties.
            run_properties = self.run.properties
            self.run.add_properties({key: val for key, val in properties.items() if key not in run_properties})

    @track(_get_logger)
    def upload_run_output(self, component, working_dir):
        if self.run:
            print('%s: upload [ %s ] outputs to run history starting...' % (RUN_RELEASE_LOG, component.name))
            # Upload output to experiment
            for output_port_name in component.outputs.keys():
                output_port_path = os.path.join(working_dir, OUTPUT_DIR_NAME, output_port_name)
                if os.path.exists(output_port_path):
                    if os.path.isdir(output_port_path):
                        self.run.upload_folder(output_port_name, output_port_path)
                    else:
                        self.run.upload_file(output_port_name, output_port_path)
            print('%s: upload [ %s ] outputs to run history completed...' % (RUN_RELEASE_LOG, component.name))

    @track(_get_logger)
    def upload_folder(self, folder):
        if self.run:
            if Path(folder).exists():
                print('%s: upload %s to run history starting...' % (RUN_RELEASE_LOG, folder))
                # Upload output to experiment
                self.run.upload_folder(os.path.basename(folder), folder)
                print('%s: upload %s to run history completed...' % (RUN_RELEASE_LOG, folder))
            else:
                print('%s: Warning, cannot find the folder %s to upload to run history.' % (RUN_RELEASE_LOG, folder))

    @track(_get_logger)
    def upload_snapshot(self, snapshot_path):
        if self.track_run_history and Path(snapshot_path).exists():
            # Check snapshot exists, avoid repeated upload it.
            if not self.run.get_snapshot_id():
                if Path(snapshot_path).exists():
                    print('%s: upload snapshot to run history starting...' % RUN_RELEASE_LOG)
                    total_size = 0
                    for path, dirs, files in os.walk(snapshot_path):
                        total_size += sum(os.path.getsize(os.path.join(path, file_name)) for file_name in files)
                    snapshot_client = SnapshotsClient(self.run._experiment.workspace)
                    snapshot_id = snapshot_client.create_snapshot(snapshot_folder=snapshot_path, size=total_size)
                    self.add_properties({PropertyKeys.SNAPSHOT_ID: snapshot_id})
                    print('%s: upload snapshot to run history completed...' % RUN_RELEASE_LOG)
                else:
                    print('%s: Warning, cannot find the snapshot %s to upload to run history.' %
                          (RUN_RELEASE_LOG, snapshot_path))

    @track(_get_logger)
    def upload_run_log(self, log_file_name, log_file_path):
        log_file_url = None
        if self.run and Path(log_file_path).exists():
            upload_log_file = self.run.upload_file(log_file_name, log_file_path)
            log_file_url = upload_log_file.artifact_content_information[log_file_name].content_uri
        return log_file_url

    @track(_get_logger)
    def append_run_history_log(self, message):
        """Append message to run history log."""
        if self.run and hasattr(self, 'run_history_log_info'):
            run = self.run
            _run_artifacts_client = run._experiment.workspace.service_context._get_artifacts_restclient().artifact
            url = _run_artifacts_client.upload.metadata['url']
            path_format_arguments = {
                'subscriptionId': run._experiment.workspace.subscription_id,
                'resourceGroupName': run._experiment.workspace.resource_group,
                'workspaceName': run._experiment.workspace.name,
                'origin': 'ExperimentRun',
                'container': run._container,
                'path': self.run_history_log_info.path
            }
            url = _run_artifacts_client._client.format_url(url, **path_format_arguments)
            query_parameters = {'append': True}
            header_parameters = {'Content-Type': 'application/octet-stream'}
            request = _run_artifacts_client._client.post(url, query_parameters)
            response = _run_artifacts_client._client.send(
                request, header_parameters, message.encode('utf-8'), stream=False)

            if response.status_code not in [200]:
                raise ErrorResponseException(_run_artifacts_client._serialize, response)

    @track(_get_logger)
    def create_run_history_log(self, path):
        """
        Create and get run history log.

        :param path: Run history log path.
        :type path: str
        """
        if self.run:
            run = self.run
            from azureml._restclient.models.artifact_dto import ArtifactDto
            _run_artifacts_client = run._experiment.workspace.service_context._get_artifacts_restclient().artifact
            artifact_dto = ArtifactDto(origin='ExperimentRun', container=run._container, path=path)
            # Create run artifact
            _run_artifacts_client.create(
                subscription_id=run._experiment.workspace.subscription_id,
                resource_group_name=run._experiment.workspace.resource_group,
                workspace_name=run._experiment.workspace.name,
                artifact_dto=artifact_dto)
            # Get run artifact info
            result = _run_artifacts_client.get_content_information(
                subscription_id=run._experiment.workspace.subscription_id,
                resource_group_name=run._experiment.workspace.resource_group,
                workspace_name=run._experiment.workspace.name,
                origin='ExperimentRun',
                container=run._container,
                path=path,
                raw=True
            )
            self.run_history_log_info = result.output

    def get_run_history_log_url(self):
        if hasattr(self, 'run_history_log_info'):
            return self.run_history_log_info.content_uri
        return None

    @track(_get_logger)
    def get_child_tracker(self, name, path=None):
        """Generate child run tracker."""
        if self.track_run_history:
            return RunHistoryTracker.from_run(
                run=self.run.child_run(name=name),
                track_run_history=self.track_run_history,
                path=path)
        else:
            return RunHistoryTracker(None, track_run_history=False)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val:
            self.update_run_result_status(False, error_details=exc_val)


def get_current_run():
    # Get Run exists in current environment.
    try:
        run = CoreRun.get_context(allow_offline=False)
        return run
    except Exception:
        return None


def _get_and_start_run_with_definition(component, experiment, working_dir) -> CoreRun:
    """ Starts a run with definition.

    :param component: Executed component
    :type component: azure.ml.component.Component
    :param experiment: Experiment
    :type azuerml.core.Experiment
    :param working_dir: The output path for component output info
    :type working_dir: str
    """
    # TODO: we may need to reuse the code from _commands in the future
    # Prepare run config
    run_id = str(uuid.uuid4())
    run_config = component._populate_runconfig(run_id, use_local_compute=True)
    # Mount is not allowed with local compute
    for data_ref in run_config.data_references.values():
        data_ref.mode = 'download'
    for data in run_config.data.values():
        data.mechanism = 'download'

    try:
        return _submit_local_run_2_execution_service(component, experiment, run_config, run_id, working_dir)
    except BaseException:
        # If execution service doesn't support this kind of run, just submit an empty one.
        return CoreRun._start_logging(experiment, outputs=working_dir, snapshot_directory=None)


def _submit_local_run_2_execution_service(component, experiment, run_config, run_id, working_dir) -> CoreRun:
    import urllib3

    from azureml._restclient import RunClient
    from azureml._restclient.models import CreateRunDto
    from azureml._restclient.clientbase import ClientBase
    from azureml._execution._commands import _raise_request_error, _get_common_headers, _serialize_run_config_to_dict

    service_context = component.workspace.service_context
    service_arm_scope = "{}/experiments/{}".format(service_context._get_workspace_scope(), experiment.name)
    service_address = service_context._get_execution_url()

    definition = {
        'Configuration': _serialize_run_config_to_dict(run_config)
    }

    files = [
        ("files", ("definition.json", json.dumps(definition, indent=4, sort_keys=True)))
    ]

    headers = _get_common_headers()
    auth_header = component.workspace._auth_object.get_authentication_header()
    headers.update(auth_header)

    uri = service_address + "/execution/v1.0" + service_arm_scope + "/localrun"

    # Unfortunately, requests library does not take Queryparams nicely.
    # Appending run_id_query to the url for service to extract from it.

    run_id_query = urllib3.request.urlencode({"runId": run_id})
    uri += "?" + run_id_query

    response = ClientBase._execute_func(requests.post, uri, files=files, headers=headers)
    _raise_request_error(response, "starting run")

    # set run name with run client
    client = RunClient(service_context, experiment.name, run_id,
                       experiment_id=experiment.id)
    create_run_dto = CreateRunDto(run_id, name=component.display_name)
    run_dto = client.patch_run(create_run_dto)
    return CoreRun(experiment=experiment, run_id=run_id, outputs=working_dir, _run_dto=run_dto)
