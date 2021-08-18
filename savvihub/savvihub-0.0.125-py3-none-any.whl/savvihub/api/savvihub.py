import inspect
from functools import wraps

from openapi_client import *
from savvihub.api.exceptions import convert_to_savvihub_exception, NotFoundAPIException
from savvihub.common.constants import API_HOST, __VERSION__


def raise_savvihub_exception(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ApiException as e:
            raise convert_to_savvihub_exception(e)

    return wrapped


def decorate_all_methods(method_decorator):
    def class_decorator(cls):
        for attr in inspect.classify_class_attrs(cls):
            if attr.kind == 'method' and issubclass(attr.defining_class, cls.__bases__[0]):
                setattr(cls, attr.name, method_decorator(attr[3]))
        return cls
    return class_decorator


@decorate_all_methods(raise_savvihub_exception)
class OpenAPIClientWithSavviHubException(APIV1Api):
    pass


class SavviHubClient:
    def __init__(self, *, auth_header=None, api_host=API_HOST):
        api_configuration = Configuration(host=api_host)
        # disable verify ssl (https://github.com/urllib3/urllib3/issues/1682#issuecomment-533311857)
        api_configuration.verify_ssl = False
        api_configuration.client_side_validation = False
        import urllib3
        urllib3.disable_warnings()

        _api_client = ApiClient(configuration=api_configuration)
        if auth_header:
            self.auth_header = auth_header
            for header_name, header_value in auth_header.items():
                _api_client.default_headers[header_name] = header_value

        _api_client.default_headers['X-Version'] = __VERSION__

        self.client = OpenAPIClientWithSavviHubException(_api_client)

    def signup_for_test_only(self, email, username, name, password, invitation_token) -> ResponseUserWithTokenResponse:
        return self.client.sign_up_api(
            sign_up_api_payload=SignUpAPIPayload(
                email=email,
                username=username,
                name=name,
                password=password,
                invitation_token=invitation_token,
            ),
        )

    def signin_confirm_for_test_only(self, cli_token):
        return self.client.sign_in_cli_confirm_api(
            sign_in_cli_confirm_api_payload=SignInCliConfirmAPIPayload(
                cli_token=cli_token,
            ),
        )

    def get_my_info(self) -> ResponseMyUser:
        return self.client.get_my_user_info_api()

    def region_list(self) -> RegionRegionListResponse:
        return self.client.region_list_api()

    def verify_access_token(self):
        self.client.access_token_verify_api()

    def experiment_id_read(self, experiment_id) -> ResponseExperimentInfo:
        return self.client.experiment_read_by_idapi(experiment_id=experiment_id)

    def project_read(self, organization_name, project_name) -> ResponseProjectInfo:
        return self.client.project_read_api(organization_name=organization_name, project_name=project_name)

    def signin_cli_token(self) -> AccountSignInCliTokenResponse:
        return self.client.sign_in_cli_token_api()

    def check_signin(self, cli_token) -> AccountSignInCliCheckResponse:
        return self.client.sign_in_cli_check_api(cli_token=cli_token)

    def github_token(self) -> ExternalCliGitHubTokenResponse:
        return self.client.cli_git_hub_token_api()

    def volume_read(self, volume_id) -> ResponseVolume:
        return self.client.volume_read_api(volume_id=volume_id)

    def volume_file_list(
        self, volume_id, path='', recursive=False, need_download_url=False,
    ) -> VolumeVolumeFileListResponse:
        return self.client.volume_file_list_api(
            volume_id=volume_id,
            path=path,
            recursive=recursive,
            need_download_url=need_download_url,
        )

    def volume_file_read(self, volume_id, path) -> ResponseFileMetadata:
        return self.client.volume_file_read_api(volume_id=volume_id, path=path)

    def volume_file_copy(self, volume_id, source_path, dest_path, recursive=False) -> VolumeVolumeFileCopyResponse:
        return self.client.volume_file_copy_api(
            volume_id=volume_id,
            volume_file_copy_api_payload=VolumeFileCopyAPIPayload(
                source_path=source_path,
                source_dataset_version='latest',
                dest_path=dest_path,
                recursive=recursive,
            ),
        )

    def volume_file_delete(self, volume_id, path, recursive=False) -> VolumeVolumeFileDeleteResponse:
        return self.client.volume_file_delete_api(volume_id=volume_id, path=path, recursive=recursive)

    def volume_file_create(self, volume_id, path, is_dir) -> ResponseFileMetadata:
        return self.client.volume_file_create_api(
            volume_id=volume_id,
            volume_file_create_api_payload=VolumeFileCreateAPIPayload(
                path=path,
                is_dir=is_dir,
            ),
        )

    def volume_file_uploaded(self, volume_id, path) -> ResponseFileMetadata:
        return self.client.volume_file_uploaded_api(
            volume_id=volume_id,
            path=path,
        )

    def dataset_version_read(self, dataset_id, dataset_version_hash) -> ResponseDatasetVersionInfo:
        return self.client.dataset_version_read_api(dataset_id=dataset_id, dataset_version_hash=dataset_version_hash)

    def sweep_list(self, organization, project) -> SweepSweepListResponse:
        return self.client.sweep_list_api(
            organization_name=organization,
            project_name=project,
        )

    def sweep_read(self, organization, project, sweep):
        return self.client.sweep_read_api(
            organization_name=organization,
            project_name=project,
            sweep=sweep,
        )

    def sweep_create(
        self, organization, project, objective, algorithm, search_space, parallel_experiment_count,
        max_experiment_count, max_failed_experiment_count, message, cluster_name, image_url, resource_spec_id,
        resource_spec, start_command, env_vars, volume_mounts,
    ) -> ResponseSweepInfo:
        return self.client.sweep_create_api(
            organization_name=organization,
            project_name=project,
            sweep_create_api_payload=SweepCreateAPIPayload(
                objective=objective,
                algorithm=algorithm,
                search_space=search_space,
                parallel_experiment_count=parallel_experiment_count,
                max_experiment_count=max_experiment_count,
                max_failed_experiment_count=max_failed_experiment_count,
                message=message,
                cluster_name=cluster_name,
                image_url=image_url,
                resource_spec_id=resource_spec_id,
                resource_spec=resource_spec,
                env_vars=env_vars,
                start_command=start_command,
                volumes=volume_mounts,
            ),
        )

    def sweep_stop(self, organization, project, sweep) -> ResponseSweepInfo:
        return self.client.sweep_terminate_api(
            organization_name=organization,
            project_name=project,
            sweep=sweep,
        )

    def sweep_logs(self, organization, project, sweep, **kwargs) -> SweepSweepLogsResponse:
        return self.client.sweep_logs_api(
            organization_name=organization,
            project_name=project,
            sweep=sweep,
            **kwargs,
        )

    def experiment_read(self, organization, project, experiment_number_or_name) -> ResponseExperimentInfo:
        return self.client.experiment_read_api(
            organization_name=organization,
            project_name=project,
            experiment=experiment_number_or_name,
        )

    def experiment_list(self, organization, project) -> ExperimentExperimentListResponse:
        return self.client.experiment_list_by_project_api(
            organization_name=organization,
            project_name=project,
            order_field='id',
            order_direction='desc',
        )

    def experiment_logs(self, organization, project, experiment_number_or_name, **kwargs) -> ExperimentExperimentLogsResponse:
        return self.client.experiment_logs_api(
            organization_name=organization,
            project_name=project,
            experiment=experiment_number_or_name,
            **kwargs,
        )

    def experiment_create(
        self, organization, project, message, cluster_name, image_url, resource_spec_id, resource_spec,
        start_command, env_vars, volume_mounts,
    ) -> ResponseExperimentInfo:
        return self.client.experiment_create_api(
            organization_name=organization,
            project_name=project,
            experiment_create_api_payload=ExperimentCreateAPIPayload(
                message=message,
                cluster_name=cluster_name,
                image_url=image_url,
                resource_spec_id=resource_spec_id,
                resource_spec=resource_spec,
                env_vars=env_vars,
                start_command=start_command,
                volumes=volume_mounts,
            ),
        )

    def experiment_plots_metrics_update(self, experiment_id, metrics):
        self.client.cli_experiment_plots_metrics_update_api(
            experiment_id=experiment_id,
            cli_experiment_plots_metrics_update_api_payload=CliExperimentPlotsMetricsUpdateAPIPayload(
                metrics=metrics,
            ),
        )

    def experiment_plots_files_update(self, experiment_id, files, type):
        self.client.cli_experiment_plots_files_update_api(
            experiment_id=experiment_id,
            cli_experiment_plots_files_update_api_payload=CliExperimentPlotsFilesUpdateAPIPayload(
                files=files,
                type=type,
            )
        )

    def kernel_image_list(self, organization) -> KernelKernelImageListResponse:
        return self.client.kernel_image_list_api(organization_name=organization)

    def kernel_resource_list(self, organization) -> KernelKernelResourceSpecListResponse:
        return self.client.kernel_resource_spec_list_api(organization_name=organization)

    def organization_list(self) -> OrganizationOrganizationListResponse:
        return self.client.organization_list_api()

    def organization_read(self, organization) -> ResponseOrganization:
        return self.client.organization_read_api(organization_name=organization)

    def organization_create(self, organization_name, region) -> ResponseOrganization:
        return self.client.organization_create_api(
            organization_create_api_payload=OrganizationCreateAPIPayload(
                name=organization_name,
                region=region,
            ),
        )

    def project_list(self, organization_name) -> ResponseProjectListResponse:
        return self.client.project_list_api(organization_name=organization_name)

    def public_dataset_list(self) -> ResponseDatasetInfoList:
        return self.client.datasets_public_list_api()

    def dataset_list(self, organization) -> ResponseDatasetInfoList:
        return self.client.dataset_list_api(organization_name=organization)

    def dataset_read(self, organization_name, dataset_name) -> ResponseDatasetInfo:
        try:
            return self.client.dataset_read_api(organization_name=organization_name, dataset_name=dataset_name)
        except NotFoundAPIException:
            raise NotFoundAPIException(f'Dataset `{dataset_name}` is not in the organization `{organization_name}`.')

    def dataset_create(self, organization, name, is_version_enabled, description) -> ResponseDatasetInfo:
        return self.client.savvi_hub_dataset_create_api(
            organization_name=organization,
            savvi_hub_dataset_create_api_payload=SavviHubDatasetCreateAPIPayload(
                name=name,
                is_version_enabled=is_version_enabled,
                description=description,
            ),
        )

    def dataset_gs_create(self, organization, name, is_public, description, gs_path) -> ResponseDatasetInfo:
        return self.client.g_s_dataset_create_api(
            organization_name=organization,
            gs_dataset_create_api_payload=GSDatasetCreateAPIPayload(
                name=name,
                is_public=is_public,
                description=description,
                gs_path=gs_path,
            ),
        )

    def dataset_s3_create(self, organization, name, is_public, description, s3_path, aws_role_arn, is_version_enabled, version_s3_path) -> ResponseDatasetInfo:
        return self.client.s3_dataset_create_api(
            organization_name=organization,
            s3_dataset_create_api_payload=S3DatasetCreateAPIPayload(
                name=name,
                is_public=is_public,
                description=description,
                s3_path=s3_path,
                aws_role_arn=aws_role_arn,
                is_version_enabled=is_version_enabled,
                version_s3_path=version_s3_path,
            ),
        )

    def cluster_list(self, organization_name) -> ClusterAllClusterListResponse:
        return self.client.all_cluster_list_api(organization_name=organization_name)

    def cluster_delete(self, organization_name, cluster_name):
        self.client.custom_cluster_delete_api(organization_name=organization_name, cluster_name=cluster_name)

    def cluster_rename(self, organization_name, cluster_name, new_name) -> ResponseKernelCluster:
        return self.client.custom_cluster_update_api(
            organization_name=organization_name,
            cluster_name=cluster_name,
            custom_cluster_update_api_payload=CustomClusterUpdateAPIPayload(
                name=new_name,
            ),
        )

    def cluster_node_list(self, organization_name, cluster_name) -> ClusterCustomClusterNodeListResponse:
        return self.client.custom_cluster_node_list_api(
            organization_name=organization_name,
            cluster_name=cluster_name
        )

    def ssh_key_add(self, public_key, name, filename) -> ResponseSSHKeyInfo:
        return self.client.s_sh_key_create_api(
            ssh_key_create_api_payload=SSHKeyCreateAPIPayload(
                public_key=public_key,
                name=name,
                filename=filename,
            ),
        )

    def ssh_key_list(self) -> AccountSSHKeyListResponse:
        return self.client.s_sh_key_list_api()

    def ssh_key_delete(self, ssh_key_id):
        return self.client.s_sh_key_delete_api(ssh_key_id)

    def workspace_list(self, organization_name, status, mine=True) -> WorkspaceWorkspaceListResponse:
        return self.client.workspace_list_api(
            organization_name,
            mine=mine,
            status=status,
        )

    def workspace_read(self, organization_name, workspace_id) -> ResponseWorkspaceDetail:
        return self.client.workspace_read_api(
            organization_name,
            workspace_id=workspace_id,
        )

    def workspace_update_backup_dt(self, workspace_id) -> WorkspaceCliWorkspaceBackupResponse:
        return self.client.cli_workspace_backup_api(
            workspace_id=workspace_id,
        )
