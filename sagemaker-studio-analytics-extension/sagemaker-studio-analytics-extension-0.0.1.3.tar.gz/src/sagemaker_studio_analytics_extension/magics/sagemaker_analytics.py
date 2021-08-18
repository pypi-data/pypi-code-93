# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from __future__ import print_function

import json
import logging
import os
import subprocess
import sys
from time import sleep
from uuid import uuid4

import IPython
import boto3
import botocore
import filelock
from IPython import get_ipython
from IPython.core.display import display
from IPython.core.magic import (
    Magics,
    magics_class,
    line_magic,
)
from IPython.core.magic_arguments import magic_arguments, argument, parse_argstring
import sparkmagic.utils.configuration as conf

# The class MUST call this class decorator at creation time
# https://ipython.readthedocs.io/en/stable/config/custommagics.html
from ipywidgets import widgets
from requests_kerberos import REQUIRED
from sagemaker_studio_sparkmagic_lib.emr import EMRCluster
from sagemaker_studio_sparkmagic_lib.kerberos import write_krb_conf
from sparkmagic.utils.constants import LANG_SCALA, LANG_PYTHON

IPYTHON_KERNEL = "IPythonKernel"
PYSPARK_KERNEL = "PySparkKernel"
SUCCESS = "SUCCESS"
FAILURE = "FAILURE"
LIBRARY_NAME = "sagemaker-analytics"
LANGUAGES_SUPPORTED = {LANG_SCALA, LANG_PYTHON}
SUPPORTED_SERVICES = {"emr"}
SUPPORTED_OPERATIONS = {"connect"}
AUTH_TYPE_SET = {"Kerberos", "None", "Basic_Access"}
KRB_FILE_DIR = "/etc"
KRB_FILE_PATH = os.path.join(KRB_FILE_DIR, "krb5.conf")
SPARK_SESSION_NAME_PREFIX = "sagemaker_studio_analytics_spark_session"

# Livy default port
# https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-web-interfaces.html
LIVY_DEFAULT_PORT = "8998"

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))

"""
This method handles connectivity to EMR clusters from PySpark and SparkScala kernels
"""


def _magic_kernel_connect_to_emr(
    emr_client, args, emr_cluster, username, password, kernel_name
):
    # TODO: test against spark scala kernel
    print("Initiating EMR connection..")
    ipy = get_ipython()
    _run_preset_cell_magics(ipy)

    endpoint_magic_line = _get_endpoint_magic_line(
        emr_client, args, emr_cluster, username, password, kernel_name
    )

    _handle_kerberos_endpoint_override(emr_cluster=emr_cluster)

    # Pass the livy endpoint to connect to, through the internal cell magic without spark.conf
    change_endpoint_magic = ipy.find_line_magic("_do_not_call_change_endpoint")
    change_endpoint_magic(endpoint_magic_line)

    # Start spark session
    start_session_magic = ipy.find_cell_magic("_do_not_call_start_session")
    start_session_magic("")

    # TODO: Find a way to establish actual success of spark session establishment, before assigning success code and
    #  error message, across kernels
    _echo_response_to_iopub_web_socket(
        _build_response(
            cluster_id=args.cluster_id,
            error_message=None,
            success=True,
            service="emr",
            operation="connect",
        )
    )


def _get_endpoint_magic_line(
    emr_client, args, emr_cluster, username, password, kernel_name
):
    livy_host = emr_cluster.primary_node_private_dns_name()
    livy_port = _get_livy_port(
        args=args, emr_client=emr_client, emr_cluster=emr_cluster
    )

    livy_endpoint = "http://{0}:{1}".format(livy_host, livy_port)
    if kernel_name == PYSPARK_KERNEL:
        return _get_pyspark_kernel_endpoint_magic_line(
            args=args,
            livy_endpoint=livy_endpoint,
            username=username,
            password=password,
        )

    return _get_ipython_kernel_endpoint_magic_line(
        args=args,
        livy_endpoint=livy_endpoint,
        username=username,
        password=password,
    )


def _get_livy_port(args, emr_client, emr_cluster):
    livy_port = LIVY_DEFAULT_PORT

    livy_port_from_cluster_configuration = _get_livy_port_from_cluster_configuration(
        emr_cluster=emr_cluster,
    )
    if livy_port_from_cluster_configuration:
        livy_port = livy_port_from_cluster_configuration
    else:
        livy_port_from_instance_group = _get_livy_port_from_instance_group(
            emr_client=emr_client,
            args=args,
        )
        if livy_port_from_instance_group:
            livy_port = livy_port_from_instance_group
    return livy_port


def _run_preset_cell_magics(ipy):
    # To allow retry on user errors without kernel restart
    allow_retry_fatal = ipy.find_cell_magic("_do_not_call_allow_retry_fatal")
    allow_retry_fatal("")
    # To delete existing sessions before creating a new one for eac astra connect
    # This is to prevent any race conditions that may arise because of session reuse
    delete_session_magic = ipy.find_cell_magic("_do_not_call_delete_session")
    delete_session_magic("")


def _get_lock():
    """
    Handle cases when same studio user tries to connect to multiple kerberos clusters across notebooks.
    Because the krb5.conf location is same, this lock prevents async modifications to the file till one
    connection either succeeds or fails For same EMR cluster across notebooks, spark magic will hold off
    one initiating a session till the parallel session from another notebook is initiated or fails
    """
    lock = filelock.FileLock("{0}.lock".format(KRB_FILE_PATH))
    if lock.is_locked:
        logger.debug("Lock is already acquired, waiting for 15s to check again")
        # Try to handle an unexpected kernel crash case
        sleep(15)
        # Check if lock is still locked
        if lock.is_locked:
            # Force release the lock as the kernel might have died silently
            logger.debug(
                "Lock is still acquired after wait, trying to force release lock before attempting "
                "to acquire for processing"
            )
            lock.release(force=True)
    return lock


def _get_credentials_and_connect(emr_client, args, emr_cluster, kernel_name):
    username = widgets.Text(
        value="", placeholder="", description="Username:", disabled=False
    )
    password = widgets.Password(
        value="", placeholder="Enter password", description="Password:", disabled=False
    )
    display(username, password)
    button = widgets.Button(
        description="Connect",
        disabled=False,
        button_style="",
        tooltip="Connect to EMR",
        icon="",
    )
    output = widgets.Output()
    display(button, output)

    # Do not remove the unused param otherwise the button will become unresponsive
    def _on_button_clicked(b):
        with output:
            if args.auth_type == "Basic_Access":
                _initiate_connect_based_on_kernel(
                    emr_client=emr_client,
                    args=args,
                    emr_cluster=emr_cluster,
                    username=username.value,
                    password=password.value,
                    kernel_name=kernel_name,
                )
            else:
                # At this point lock should be available to acquire if another process has not already taken it
                # Go ahead and try to use the "with" context directly
                with _get_lock().acquire(
                    # Try for 15 seconds to acquire the lock, otherwise fail with lock acquire failure
                    timeout=15
                ):
                    completed_process = _generate_kerberos_token(
                        emr_cluster=emr_cluster, username=username, password=password
                    )
                    if completed_process.returncode == 0:
                        _initiate_connect_based_on_kernel(
                            emr_client=emr_client,
                            args=args,
                            emr_cluster=emr_cluster,
                            username=None,
                            password=None,
                            kernel_name=kernel_name,
                        )
                    else:
                        _handle_kerberos_connectivity_failure(
                            args=args, completed_process=completed_process
                        )

    button.on_click(_on_button_clicked)


def _generate_kerberos_token(emr_cluster, username, password):
    # noinspection PyTypeChecker
    write_krb_conf(emr_cluster, KRB_FILE_PATH)
    cmd = ["kinit", username.value.encode()]
    completed_process = subprocess.run(
        cmd,
        input=password.value.encode(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed_process


def _handle_kerberos_connectivity_failure(args, completed_process):
    error_message = None
    if completed_process.stderr:
        error_message = str(completed_process.stderr, "UTF-8")

    _echo_response_to_iopub_web_socket(
        _build_response(
            cluster_id=args.cluster_id,
            error_message=error_message,
            success=False,
            service="emr",
            operation="connect",
        )
    )

    if error_message:
        raise Exception(
            "Failed to generate kerberos token using provided credentials. \n{} \n{}".format(
                error_message, str(completed_process.stdout, "UTF-8")
            )
        )


def _get_pyspark_kernel_endpoint_magic_line(args, livy_endpoint, username, password):
    if args.auth_type == "Basic_Access":
        return "-s {0} -t {1} -u {2} -p {3}".format(
            livy_endpoint, args.auth_type, username, password
        )
    else:
        return "-s {0} -t {1}".format(livy_endpoint, args.auth_type)


def _get_ipython_kernel_endpoint_magic_line(args, livy_endpoint, username, password):
    # Choice of uuid generator based on: https://docs.python.org/3/library/uuid.html
    session_name = "{0}_{1}".format(SPARK_SESSION_NAME_PREFIX, uuid4().hex)

    if args.auth_type == "Basic_Access":
        return "add -s {0} -l {1} -t {2} -u {3} -a {4} -p {5}".format(
            session_name,
            args.language,
            args.auth_type,
            livy_endpoint,
            username,
            password,
        )
    else:
        return "add -s {0} -l {1} -t {2} -u {3}".format(
            session_name, args.language, args.auth_type, livy_endpoint
        )


def _get_livy_port_from_instance_group(emr_client, args):
    """
    Check if livy port is overridden as an EMR instance group override This case will happen when the describe
    cluster response does not have livy port as cluster conf but in individual instance group configuration
    """
    emr_instance_group_list = _list_instance_groups(emr_client, args.cluster_id)
    for instance_group in emr_instance_group_list:
        # TODO: Test with multi-name-node configuration to see if livy server port is set to all master nodes or not
        if instance_group["InstanceGroupType"] == "MASTER":
            instance_group_configuration_list = instance_group.get("Configurations")
            for configuration in instance_group_configuration_list:
                livy_port_override = _get_livy_port_override(configuration)
                if livy_port_override:
                    return livy_port_override


def _get_livy_port_override(configuration):
    if (
        "Classification" in configuration
        and configuration["Classification"] == "livy-conf"
        and "Properties" in configuration
    ):
        """
        There are two cases when livy port is overridden post start and on-create
        In both cases the livy port appears in different places in the describe-cluster response
        It can either be in cluster config or instance group config
        """
        livy_properties = configuration["Properties"]
        if "livy.server.port" in livy_properties:
            livy_overridden_port = livy_properties["livy.server.port"]
            return livy_overridden_port


def _ipython_kernel_connect_to_emr(
    emr_client, args, emr_cluster, username, password, kernel_name
):
    print("Initiating EMR connection..")

    ipy = get_ipython()
    # Depth should be 2 if run_line_magic is being called from within a magic
    ipy.run_line_magic("load_ext", "sparkmagic.magics", 2)
    endpoint_magic_line = _get_endpoint_magic_line(
        emr_client, args, emr_cluster, username, password, kernel_name
    )

    _handle_kerberos_endpoint_override(emr_cluster=emr_cluster)

    ipy.run_line_magic("spark", "cleanup")
    ipy.run_line_magic("spark", endpoint_magic_line)

    _echo_response_to_iopub_web_socket(
        _build_response(
            cluster_id=args.cluster_id,
            error_message=None,
            success=True,
            service="emr",
            operation="connect",
        )
    )


# External KDC use cases require the kerberos endpoint to be overridden
def _handle_kerberos_endpoint_override(emr_cluster):
    if emr_cluster.krb_hostname_override():
        # Kerberos endpoint is overridden
        overridden_kerberos_auth_config = {
            "mutual_authentication": REQUIRED,
            "hostname_override": emr_cluster.krb_hostname_override(),
        }

        # Override kerberos auth config with new KDC endpoint
        conf.override(
            conf.kerberos_auth_configuration.__name__, overridden_kerberos_auth_config
        )


def _get_livy_port_from_cluster_configuration(emr_cluster):
    emr_configuration_list = emr_cluster.__dict__.get("_cluster").get("Configurations")
    # For cluster configuration
    for configuration in emr_configuration_list:
        livy_port_override = _get_livy_port_override(configuration)
        if livy_port_override:
            return livy_port_override


def _validate_emr_args(args, usage, kernel_name):
    if args.cluster_id is None:
        raise ValueError(
            "Missing required argument '{}'. {}".format("--cluster_id", usage)
        )
    elif args.auth_type is None:
        raise ValueError(
            "Missing required argument '{}'. {}".format("--auth_type", usage)
        )
    elif args.auth_type not in AUTH_TYPE_SET:
        raise Exception(
            "Invalid auth type, supported auth types are '{}'. {}".format(
                AUTH_TYPE_SET, usage
            )
        )

    # Only IPython kernel needs language option support
    if kernel_name == IPYTHON_KERNEL:
        if args.language is None:
            raise ValueError(
                "Missing required argument '{}' for IPython kernel. {}".format(
                    "--language", usage
                )
            )
        elif args.language not in LANGUAGES_SUPPORTED:
            raise Exception(
                "Invalid language, supported languages are '{}'. {}".format(
                    LANGUAGES_SUPPORTED, usage
                )
            )


def _initiate_emr_connect(args, boto_session, kernel_name):
    # Needs EMR list instance group permissions
    emr_client = boto_session.client("emr")

    cluster = EMRCluster(cluster_id=args.cluster_id)
    _validate_cluster_auth_with_auth_type_provided(
        auth_type=args.auth_type, emr_cluster=cluster
    )

    if cluster.is_krb_cluster or args.auth_type == "Basic_Access":
        _get_credentials_and_connect(
            emr_client=emr_client,
            args=args,
            emr_cluster=cluster,
            kernel_name=kernel_name,
        )
    else:
        _initiate_connect_based_on_kernel(
            emr_client=emr_client,
            args=args,
            emr_cluster=cluster,
            username=None,
            password=None,
            kernel_name=kernel_name,
        )


def _initiate_connect_based_on_kernel(
    emr_client, args, emr_cluster, username, password, kernel_name
):
    if kernel_name == PYSPARK_KERNEL:
        _magic_kernel_connect_to_emr(
            emr_client=emr_client,
            args=args,
            emr_cluster=emr_cluster,
            username=username,
            password=password,
            kernel_name=kernel_name,
        )

    elif kernel_name == IPYTHON_KERNEL:
        _ipython_kernel_connect_to_emr(
            emr_client=emr_client,
            args=args,
            emr_cluster=emr_cluster,
            username=username,
            password=password,
            kernel_name=kernel_name,
        )


def _validate_cluster_auth_with_auth_type_provided(auth_type, emr_cluster):
    is_cluster_kerberos_authenticated = emr_cluster.is_krb_cluster
    is_cluster_ldap_authenticated = _is_cluster_ldap(emr_cluster)
    is_cluster_no_auth = (
        not is_cluster_ldap_authenticated and not is_cluster_kerberos_authenticated
    )
    # Check if auth type is kerberos or not
    if (
        (auth_type == "None" and is_cluster_kerberos_authenticated)
        or (auth_type == "Basic_Access" and is_cluster_kerberos_authenticated)
        or (auth_type == "None" and is_cluster_ldap_authenticated)
        or (auth_type == "Kerberos" and is_cluster_ldap_authenticated)
        or (auth_type == "Basic_Access" and is_cluster_no_auth)
        or (auth_type == "Kerberos" and is_cluster_no_auth)
    ):
        raise Exception(
            "Cluster auth type does not match provided auth {}".format(auth_type)
        )


def _check_required_args(args, usage):
    if args is None or args.command is None or len(args.command) != 2:
        raise Exception(
            "Please provide service name and operation to perform. {}".format(usage)
        )


def _is_cluster_ldap(cluster):
    emr_configuration_list = cluster.__dict__.get("_cluster").get("Configurations")
    if emr_configuration_list is None or not emr_configuration_list:
        return False

    # For cluster configuration
    for configuration in emr_configuration_list:
        if (
            "Classification" in configuration
            and configuration["Classification"] == "livy-conf"
            and "Properties" in configuration
        ):
            livy_properties = configuration["Properties"]
            if "livy.server.auth.type" in livy_properties:
                livy_server_auth_type = livy_properties["livy.server.auth.type"]
                if livy_server_auth_type == "ldap":
                    return True
    return False


@magics_class
class SagemakerAnalytics(Magics):
    @line_magic
    @magic_arguments()
    @argument(
        "command",
        type=str,
        default=[""],
        nargs="*",
        help="Command to execute. The command consists of a service name followed by a ' ' followed by an operation. "
        "Supported services are {0} and supported operations are {1}. For example a valid command is '{2}'.".format(
            SUPPORTED_SERVICES, SUPPORTED_OPERATIONS, "emr connect"
        ),
    )
    @argument(
        "--auth_type",
        type=str,
        default=None,
        help="The authentication type to be used. Supported authentication types are {0}.".format(
            AUTH_TYPE_SET
        ),
    )
    @argument(
        "--cluster_id",
        type=str,
        default=None,
        help="The cluster id to connect to.",
    )
    @argument(
        "--language",
        type=str,
        default=None,
        help="Language to use. The supported languages for IPython kernel(s) are {0}. This is a required "
        "argument for IPython kernels, but not for magic kernels such as PySpark or SparkScala.".format(
            LANGUAGES_SUPPORTED
        ),
    )
    def sm_analytics(self, line):
        usage = "Please look at usage of %sm_analytics by executing `%sm_analytics?`."
        user_input = line
        args = parse_argstring(self.sm_analytics, user_input)

        _check_required_args(args, usage)

        service = args.command[0].lower()
        operation = args.command[1].lower()

        # emr
        if service == "emr":
            if operation == "connect":
                try:
                    kernel_name = type(IPython.Application.instance().kernel).__name__
                    _validate_emr_args(args=args, usage=usage, kernel_name=kernel_name)

                    # Only create boto session if absolutely needed
                    boto_session = _get_boto3_session()
                    _initiate_emr_connect(
                        args=args, boto_session=boto_session, kernel_name=kernel_name
                    )
                except Exception as e:
                    _echo_response_to_iopub_web_socket(
                        _build_response(
                            cluster_id=args.cluster_id,
                            error_message=str(e),
                            success=False,
                            service=service,
                            operation=operation,
                        )
                    )
                    raise e
            else:
                raise Exception("Operation '{}' not found. {}".format(operation, usage))
        else:
            raise Exception("Service '{}' not found. {}".format(service, usage))


# In order to actually use these magics, you must register them with a
# running IPython.
def load_ipython_extension(ipython):
    """
    Any module file that define a function named `load_ipython_extension`
    can be loaded via `%load_ext module.path` or be configured to be
    auto-loaded by IPython at startup time.
    """
    # You can register the class itself without instantiating it.  IPython will
    # call the default constructor on it.
    ipython.register_magics(SagemakerAnalytics)


def _get_boto3_session():
    return boto3.session.Session()


def _list_instance_groups(emr_client, cluster_id):
    try:
        emr_instance_group_list = []
        paginator = emr_client.get_paginator("list_instance_groups")
        operation_parameters = {"ClusterId": cluster_id}
        page_iterator = paginator.paginate(**operation_parameters)
        for page in page_iterator:
            emr_instance_group_list.extend(page["InstanceGroups"])

    except botocore.exceptions.ClientError as ce:
        logger.debug(
            "Failed to list instance groups for EMR cluster({0}). {1}".format(
                cluster_id, ce.response
            )
        )
        raise ValueError(
            "Unable to list instance groups for EMR cluster(Id: {0}) using ListInstanceGroups API. Error: {1}".format(
                cluster_id, ce.response["Error"]
            )
        ) from None
    logger.debug("List instance groups response: {0}".format(emr_instance_group_list))
    return emr_instance_group_list


def _echo_response_to_iopub_web_socket(response):
    print(json.dumps(response))


def _build_response(cluster_id, error_message, success, service, operation):
    return {
        "namespace": LIBRARY_NAME,
        "cluster_id": cluster_id,
        "error_message": error_message,
        "success": success,
        "service": service,
        "operation": operation,
    }
