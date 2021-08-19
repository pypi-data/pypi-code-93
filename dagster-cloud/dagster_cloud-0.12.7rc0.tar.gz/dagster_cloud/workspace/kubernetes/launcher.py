import logging
from contextlib import contextmanager

import kubernetes
import kubernetes.client as client
from dagster import Array, Field, Noneable, StringSource, check
from dagster.builtins import String
from dagster.config.field_utils import Shape
from dagster.core.host_representation.grpc_server_registry import GrpcServerEndpoint
from dagster.serdes import ConfigurableClass
from dagster_k8s import K8sRunLauncher
from dagster_k8s.executor import K8sStepHandler
from dagster_k8s.job import DagsterK8sJobConfig
from kubernetes.client.rest import ApiException

from ..user_code_launcher import ReconcileUserCodeLauncher
from .utils import (
    SERVICE_PORT,
    construct_repo_location_deployment,
    construct_repo_location_service,
    get_unique_label_for_location,
    unique_resource_name,
    wait_for_deployment_complete,
)

DEPLOYMENT_TIMEOUT = 90  # Can take time to pull images
SERVER_TIMEOUT = 60


class K8sUserCodeLauncher(ReconcileUserCodeLauncher, ConfigurableClass):
    def __init__(
        self,
        dagster_home,
        instance_config_map,
        inst_data=None,
        namespace=None,
        kubeconfig_file=None,
        pull_policy=None,
        env_secrets=None,
        service_account_name=None,
        volume_mounts=None,
        image_pull_secrets=None,
    ):
        self._inst_data = inst_data
        self._logger = logging.getLogger("K8sUserCodeLauncher")
        self._dagster_home = check.str_param(dagster_home, "dagster_home")
        self._instance_config_map = check.str_param(instance_config_map, "instance_config_map")
        self._namespace = namespace
        self._pull_policy = pull_policy
        self._env_secrets = check.opt_list_param(env_secrets, "env_secrets", of_type=str)
        self._service_account_name = check.opt_str_param(
            service_account_name, "service_account_name"
        )
        self._volume_mounts = check.opt_list_param(volume_mounts, "volume_mounts")
        self._image_pull_secrets = check.opt_list_param(
            image_pull_secrets, "image_pull_secrets", of_type=dict
        )

        if kubeconfig_file:
            kubernetes.config.load_kube_config(kubeconfig_file)
        else:
            kubernetes.config.load_incluster_config()

        super(K8sUserCodeLauncher, self).__init__()

        self._launcher = K8sRunLauncher(
            dagster_home=self._dagster_home,
            instance_config_map=self._instance_config_map,
            postgres_password_secret=None,
            job_image=None,
            image_pull_policy=self._pull_policy,
            image_pull_secrets=self._image_pull_secrets,
            service_account_name=self._service_account_name,
            env_config_maps=None,
            env_secrets=self._env_secrets,
            job_namespace=self._namespace,
        )

    def start(self):
        super().start()
        # NOTE: for better availability, we should scan for existing servers and use them
        # (may need to check versions)
        self._cleanup_servers()

    def register_instance(self, instance):
        super().register_instance(instance)
        self._launcher.register_instance(instance)

    @property
    def inst_data(self):
        return self._inst_data

    @classmethod
    def config_type(cls):
        return {
            "dagster_home": Field(StringSource, is_required=True),
            "instance_config_map": Field(StringSource, is_required=True),
            "namespace": Field(StringSource, is_required=False, default_value="default"),
            "kubeconfig_file": Field(StringSource, is_required=False),
            "pull_policy": Field(StringSource, is_required=False, default_value="Always"),
            "env_secrets": Field(
                Noneable(Array(StringSource)),
                is_required=False,
                description="A list of custom Secret names from which to draw environment "
                "variables (using ``envFrom``) for the Job. Default: ``[]``. See:"
                "https://kubernetes.io/docs/tasks/inject-data-application/distribute-credentials-secure/#configure-all-key-value-pairs-in-a-secret-as-container-environment-variables",
            ),
            "service_account_name": Field(
                Noneable(StringSource),
                is_required=False,
                description="Override the name of the Kubernetes service account under "
                "which to run.",
            ),
            "volume_mounts": Field(
                Array(
                    Shape(
                        {
                            "name": String,
                            "path": String,
                            "sub_path": String,
                            "secret": String,
                        }
                    )
                ),
                is_required=False,
                default_value=[],
                description="Volume mounts to attach to k8s jobs",
            ),
            "image_pull_secrets": Field(
                Noneable(Array(Shape({"name": StringSource}))),
                is_required=False,
                description="Specifies that Kubernetes should get the credentials from "
                "the Secrets named in this list.",
            ),
        }

    @staticmethod
    def from_config_value(inst_data, config_value):
        return K8sUserCodeLauncher(
            dagster_home=config_value.get("dagster_home"),
            instance_config_map=config_value.get("instance_config_map"),
            inst_data=inst_data,
            namespace=config_value.get("namespace"),
            kubeconfig_file=config_value.get("kubeconfig_file"),
            pull_policy=config_value.get("pull_policy"),
            env_secrets=config_value.get("env_secrets", []),
            service_account_name=config_value.get("service_account_name"),
            volume_mounts=config_value.get("volume_mounts"),
            image_pull_secrets=config_value.get("image_pull_secrets"),
        )

    @contextmanager
    def _get_api_instance(self):
        with client.ApiClient() as api_client:
            yield client.AppsV1Api(api_client)

    def _create_deployment_endpoint(self, location_name, metadata):
        resource_name = unique_resource_name(location_name)

        try:
            with self._get_api_instance() as api_instance:
                api_response = api_instance.create_namespaced_deployment(
                    self._namespace,
                    construct_repo_location_deployment(
                        location_name,
                        resource_name,
                        metadata,
                        self._pull_policy,
                        self._env_secrets,
                        self._service_account_name,
                        self._image_pull_secrets,
                    ),
                )
            self._logger.info("Created deployment: {}".format(api_response.metadata.name))
        except ApiException as e:
            self._logger.error(
                "Exception when calling AppsV1Api->create_namespaced_deployment: %s\n" % e
            )
            raise e

        try:
            api_response = client.CoreV1Api().create_namespaced_service(
                self._namespace,
                construct_repo_location_service(location_name, resource_name),
            )
            self._logger.info("Created service: {}".format(api_response.metadata.name))
        except ApiException as e:
            self._logger.error(
                "Exception when calling AppsV1Api->create_namespaced_service: %s\n" % e
            )
            raise e

        wait_for_deployment_complete(
            resource_name,
            self._namespace,
            self._logger,
            location_name,
            metadata,
            existing_pods=[],
            timeout=DEPLOYMENT_TIMEOUT,
        )
        server_id = self._wait_for_server(
            host=resource_name, port=SERVICE_PORT, timeout=SERVER_TIMEOUT
        )

        endpoint = GrpcServerEndpoint(
            server_id=server_id,
            host=resource_name,
            port=SERVICE_PORT,
            socket=None,
        )

        return endpoint

    def _get_existing_deployments(self, location_name):
        with self._get_api_instance() as api_instance:
            return api_instance.list_namespaced_deployment(
                self._namespace,
                label_selector=f"location_hash={get_unique_label_for_location(location_name)}",
            ).items

    def _add_server(self, location_name, metadata):
        # check if the container already exists, remove it if so (could happen
        # if a previous attempt to set up the server failed)
        existing_deployments = self._get_existing_deployments(location_name)
        for existing_deployment in existing_deployments:
            self._logger.info(
                "Removing existing deployment {resource_name} for location {location_name}".format(
                    resource_name=existing_deployment.metadata.name,
                    location_name=location_name,
                )
            )
            self._remove_deployment(existing_deployment.metadata.name)

        return self._create_deployment_endpoint(location_name, metadata)

    def _gen_update_server(self, location_name, old_metadata, new_metadata):
        existing_deployments = self._get_existing_deployments(location_name)
        try:
            updated_server = self._create_deployment_endpoint(location_name, new_metadata)
            yield updated_server
        finally:
            for existing_deployment in existing_deployments:
                self._logger.info(
                    "Removing old deployment {resource_name} for location {location_name}".format(
                        resource_name=existing_deployment.metadata.name,
                        location_name=location_name,
                    )
                )
                self._remove_deployment(existing_deployment.metadata.name)

    def _remove_server(self, location_name, metadata):
        existing_deployments = self._get_existing_deployments(location_name)

        for existing_deployment in existing_deployments:
            self._remove_deployment(existing_deployment.metadata.name)

    def _remove_deployment(self, resource_name):
        check.str_param(resource_name, "resource_name")
        with self._get_api_instance() as api_instance:
            api_instance.delete_namespaced_deployment(resource_name, self._namespace)
        client.CoreV1Api().delete_namespaced_service(resource_name, self._namespace)
        self._logger.info("Removed deployment and service: {}".format(resource_name))

    def _cleanup_servers(self):
        with self._get_api_instance() as api_instance:
            deployments = api_instance.list_namespaced_deployment(
                self._namespace,
                label_selector="managed_by=K8sUserCodeLauncher",
            ).items
            for deployment in deployments:
                api_instance.delete_namespaced_deployment(deployment.metadata.name, self._namespace)

        services = (
            client.CoreV1Api()
            .list_namespaced_service(
                self._namespace,
                label_selector="managed_by=K8sUserCodeLauncher",
            )
            .items
        )
        for service in services:
            client.CoreV1Api().delete_namespaced_service(service.metadata.name, self._namespace)

        self._logger.info(
            "Deleted deployments: {} and services: {}".format(
                ",".join([deployment.metadata.name for deployment in deployments]),
                ",".join([service.metadata.name for service in services]),
            )
        )

    def __exit__(self, exception_type, exception_value, traceback):
        self._launcher.dispose()

        if self._started:
            self._cleanup_servers()

    def step_handler(self):
        return K8sStepHandler(
            job_config=DagsterK8sJobConfig(
                dagster_home=self._dagster_home,
                instance_config_map=self._instance_config_map,
                postgres_password_secret=None,
                job_image=None,
                image_pull_policy=self._pull_policy,
                image_pull_secrets=self._image_pull_secrets,
                service_account_name=self._service_account_name,
                env_config_maps=None,
                env_secrets=self._env_secrets,
                volume_mounts=self._volume_mounts,
            ),
            load_incluster_config=True,
            kubeconfig_file=None,
            job_namespace=self._namespace,
        )

    def run_launcher(self):
        return self._launcher
