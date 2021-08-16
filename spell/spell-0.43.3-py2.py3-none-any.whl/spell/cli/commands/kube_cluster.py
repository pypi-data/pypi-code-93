import click
from functools import wraps
from packaging import version
import os
import random
import subprocess
import string
import tempfile
import yaml
from spell.cli.constants import SERVING_CLUSTER_VERSION
from spell.cli.log import logger
from spell.cli.commands.cluster_aws import (
    EKS_DEFAULT_NODEGROUP_TYPE,
    eks_update,
    eks_add_arn,
    eks_delete_cluster,
)
from spell.cli.commands.cluster_gcp import (
    GKE_DEFAULT_NODEGROUP_TYPE,
    gke_add_nodepool,
    gke_scale_nodepool,
    gke_delete_nodepool,
    gke_update,
    gke_delete_cluster,
)
import spell.cli.commands.cluster_aws as cluster_aws
import spell.cli.commands.cluster_gcp as cluster_gcp
from spell.cli.utils import (
    cluster_utils,
    command,
    kube_runs,
    require_import,
    require_install,
    tabulate_rows,
)
from spell.cli.utils.command import docs_option
from spell.cli.exceptions import api_client_exception_handler, ExitException


def check_kube_cluster_exists(f):
    @wraps(f)
    def wrapped(ctx, cluster, *args, cluster_name=None, **kwargs):
        if not cluster.get("serving_cluster_name"):
            raise ExitException("No kube cluster found for model serving; cannot run this command.")
        f(ctx=ctx, *args, cluster=cluster, **kwargs)

    return wrapped


@click.group(
    name="kube-cluster",
    short_help="Manage a serving cluster",
    help="Manage a model serving kubernetes cluster (EKS or GKE)",
)
@docs_option("https://spell.ml/docs/serving_clusters/")
@click.pass_context
def kube_cluster(ctx):
    pass


@command(
    name="kubectl",
    help="Issue kubectl commands against the serving cluster",
)
@click.argument("args", nargs=-1)
@click.pass_context
@cluster_utils.pass_cluster
def kubectl(ctx, cluster, args):
    serving_cluster_name = cluster.get("serving_cluster_name")
    if not serving_cluster_name:
        click.echo("No serving cluster found!")
        return

    spell_client = ctx.obj["client"]
    with api_client_exception_handler():
        for line in spell_client.cluster_kubectl(cluster["name"], args):
            click.echo(line)


@command(
    name="create",
    short_help="Sets up a GKE/EKS kubernetes cluster in your Spell VPC. Required for model serving.",
    help="""Sets up a GKE or EKS kubernetes cluster in your Spell VPC.
    This cluster is required for model serving.
    Spell will automatically create a CPU node group for you which will have at least
    one machine running at all times.""",
)
@click.pass_context
@cluster_utils.check_cli_version
@cluster_utils.pass_cluster
@click.option("-p", "--profile", help="AWS profile to pull credentials from")
@click.option(
    "--kube-cluster-name",
    hidden=True,
    default="spell-model-serving",
    help="Name of the GKE/EKS cluster to create or the existing cluster if --use-existing",
)
@click.option(
    "--kube-cluster-domain",
    hidden=True,
    default="",
    help="If non-empty, tell the API to try to register using this as the *.spell.services subdomain",
)
@click.option(
    "--nodes-min",
    type=int,
    default=1,
    help="Minimum number of nodes in the model serving cluster (default 1)",
)
@click.option(
    "--nodes-max",
    type=int,
    default=6,
    help="Maximum number of nodes in the model serving cluster (default 6)",
)
@click.option(
    "--node-disk-size",
    type=int,
    default=50,
    help="Size of disks on each node in GB (default 50GB)",
)
@click.option(
    "--use-existing",
    is_flag=True,
    default=False,
    help="""This is an advanced option to use an existing EKS/GKE cluster instead of creating a new one.
    It will reapply kubernetes configurations. Because Spell sets up your cluster in a particular manner
    this option is only likely to work with clusters created exactly the way we set ours up. This flag
    is likely only valuable if you experienced an error the first time you tried to run this command,
    but the kube cluster creation succeeded.""",
)
@click.option(
    "--encrypt-internal-traffic",
    is_flag=True,
    default=False,
    help="Use mutual TLS on all cluster-internal traffic as a security measure",
)
@click.option(
    "--aws-zones",
    type=str,
    default=None,
    help="Allows AWS clusters to explicitly list the availability zones used for the EKS cluster. "
    "List the desired AZs as comma separated values, ex: 'us-east-1a,us-east-1c,us-east-1d'. "
    "NOTE: Most users will NOT have to do this. This is useful if there are problems with "
    "one or more of the AZs in the region of your cluster.",
)
@click.option(
    "--support-runs",
    hidden=True,
    is_flag=True,
    help="Configure this K8S cluster to support runs. Currently in development!",
)
@cluster_utils.for_aws(
    require_import("kubernetes", pkg_extras="cluster-aws"),
    require_install("eksctl", "kubectl", "aws-iam-authenticator"),
    cluster_utils.pass_aws_session(
        perms=[
            "Leverage eksctl to create an EKS cluster",
            "Leverage eksctl to create an auto scaling group to back the cluster",
        ]
    ),
)
@cluster_utils.for_gcp(
    require_import("kubernetes", "googleapiclient", pkg_extras="cluster-gcp"),
    require_install("gcloud", "kubectl"),
    cluster_utils.pass_gcp_project_creds,
    cluster_utils.handle_aws_profile_flag,
)
def create_kube_cluster(
    ctx,
    cluster,
    kube_cluster_name,
    kube_cluster_domain,
    nodes_min,
    nodes_max,
    node_disk_size,
    use_existing,
    encrypt_internal_traffic,
    aws_zones,
    support_runs,
    aws_session=None,
    gcp_project=None,
    gcp_creds=None,
):
    """
    Deploy a GKE or EKS cluster for model serving
    by auto-detecting the cluster provider.
    """
    spell_client = ctx.obj["client"]
    if ctx.obj["stack"] == "local" and not kube_cluster_name:
        raise ExitException(
            "Please use '--kube-cluster-name' flag to specify a unique K8s cluster name"
        )
    if cluster["cloud_provider"] not in ["AWS", "GCP"]:
        raise ExitException("Serving clusters can only be created in AWS and GCP Spell clusters")
    if encrypt_internal_traffic and cluster["cloud_provider"] != "AWS":
        raise ExitException("Internally encrypted traffic is not yet supported on GCP/GKE clusters")

    click.echo("Generating default node group config...")
    default_ng_config = {
        "min_nodes": nodes_min,
        "max_nodes": nodes_max,
        "disk_size_gb": node_disk_size,
    }
    if cluster["cloud_provider"] == "AWS":
        default_ng_config["instance_type"] = EKS_DEFAULT_NODEGROUP_TYPE
        default_ng_config["name"] = "default"
    if cluster["cloud_provider"] == "GCP":
        default_ng_config["instance_type"] = GKE_DEFAULT_NODEGROUP_TYPE
        default_ng_config["name"] = "default-pool"

    # NOTE(waldo) for legacy reasons 'is_public' only controls load balancer visibility for ambassador;
    # a cluster with is_public set to 'False' will use an internal load balancer for ambassador;
    # since ambassador is used as the ingress gateway for all model servers.
    # the eks/gke cluster which is created by this setup is still a public cluster in that
    # nodes are publicly addressible; however no ports should be open + accessible to an unauthenticated party
    is_public = (
        click.prompt(
            "Would you like your model servers to be public or private? "
            "Private model servers will only be accessible from within the cluster's VPC.",
            type=click.Choice(["public", "private"]),
        ).strip()
        == "public"
    )

    serving_cluster_location = ""
    if cluster["cloud_provider"] == "GCP":
        from googleapiclient import discovery

        compute_service = discovery.build("compute", "v1", credentials=gcp_creds)
        gcp_project_name = cluster["networking"]["gcp"]["project"]
        region = cluster["networking"]["gcp"]["region"]
        serving_cluster_location = cluster_gcp.get_zone_from_region(
            compute_service, gcp_project_name, region
        )

    with api_client_exception_handler():
        spell_client.register_serving_cluster(
            cluster["name"],
            SERVING_CLUSTER_VERSION,
            is_public=is_public,
            support_runs=support_runs,
            kube_config=None,
            default_ng_config=default_ng_config,
            serving_cluster_domain=kube_cluster_domain,
            serving_cluster_name=kube_cluster_name,
            serving_cluster_status="created",
            serving_cluster_location=serving_cluster_location,
        )

    # Provision the k8s serving cluster from the cloud provider
    if cluster["cloud_provider"] == "AWS":
        if use_existing:
            click.echo("Skipping EKS cluster creation, existing contexts are:")
            cluster_utils.check_kube_context()
        else:
            cluster_aws.create_eks_cluster(
                cluster,
                aws_session.profile_name,
                kube_cluster_name,
                aws_session,
                nodes_min,
                nodes_max,
                node_disk_size,
                aws_zones,
            )

    elif cluster["cloud_provider"] == "GCP":
        from googleapiclient import discovery

        gcp_project_name = cluster["networking"]["gcp"]["project"]
        region = cluster["networking"]["gcp"]["region"]
        subnet = cluster["networking"]["gcp"]["subnet"]
        network = cluster["networking"]["gcp"]["vpc"]
        service_account = cluster["role_credentials"]["gcp"]["service_account_id"]

        if not use_existing:
            cluster_gcp.create_gke_cluster(
                kube_cluster_name,
                gcp_project_name,
                service_account,
                serving_cluster_location,
                nodes_min,
                nodes_max,
                node_disk_size,
                network,
                subnet,
            )
        else:
            if not click.confirm("Are you sure you want to use {}?".format(kube_cluster_name)):
                raise ExitException(
                    "Please run without --use-existing or specify a different --kube-cluster-name"
                )
            cmd = [
                "gcloud",
                "container",
                "clusters",
                "get-credentials",
                "--project",
                gcp_project_name,
                "--zone",
                serving_cluster_location,
                kube_cluster_name,
            ]
            subprocess.check_call(cmd)

    # Generate kubeconfig
    if cluster["cloud_provider"] == "AWS":
        with tempfile.NamedTemporaryFile(mode="r", suffix=".yaml") as f:
            cmd = (
                "eksctl",
                "utils",
                "write-kubeconfig",
                "--profile",
                aws_session.profile_name,
                "--cluster",
                kube_cluster_name,
                "--kubeconfig",
                f.name,
            )
            try:
                subprocess.check_call(cmd)
            except Exception as e:
                raise ExitException("Retrieving kubeconfig failed. Error was: {}".format(e))
            kubecfg_yaml = f.read()
    elif cluster["cloud_provider"] == "GCP":
        with tempfile.NamedTemporaryFile(mode="r", suffix=".yaml") as f:
            cmd = (
                "gcloud",
                "container",
                "clusters",
                "get-credentials",
                kube_cluster_name,
                "--zone",
                serving_cluster_location,
                "--project",
                gcp_project_name,
            )
            env = os.environ.copy()
            env["KUBECONFIG"] = f.name
            try:
                subprocess.check_call(cmd, env=env)
            except Exception as e:
                raise ExitException("Retrieving kubeconfig failed. Error was: {}".format(e))
            parsed_yaml = yaml.safe_load(f)

        # update kubeconfig to use the custom `gcp-svc` auth-provider
        if (
            "users" not in parsed_yaml
            or len(parsed_yaml["users"]) != 1
            or "user" not in parsed_yaml["users"][0]
            or "auth-provider" not in parsed_yaml["users"][0]["user"]
        ):
            raise Exception("Unexpected kubeconfig yaml generated from gcloud command")
        parsed_yaml["users"][0]["user"]["auth-provider"] = {
            "name": "gcp-svc",
            "config": {"service-acct": service_account},
        }
        kubecfg_yaml = yaml.dump(parsed_yaml, default_flow_style=False)

    # update the API, again
    with api_client_exception_handler():
        spell_client.register_serving_cluster(
            cluster["name"],
            SERVING_CLUSTER_VERSION,
            is_public=is_public,
            support_runs=support_runs,
            kube_config=kubecfg_yaml,
            default_ng_config=default_ng_config,
            serving_cluster_domain=kube_cluster_domain,
            serving_cluster_name=kube_cluster_name,
            serving_cluster_status="provisioned",
        )

    # deploy run-specific infrastructure
    if support_runs:
        cluster_utils.create_namespace("spell-run")
        kube_runs.add_argo()

    # deploy infrastructure shared to runs and runs / serving
    if cluster["cloud_provider"] == "AWS":
        supported_features = cluster_aws.eks_configure_k8s(
            ctx,
            aws_session,
            cluster,
            kube_cluster_name,
            is_public,
            support_runs,
            encrypt_internal_traffic,
        )
    elif cluster["cloud_provider"] == "GCP":
        supported_features = cluster_gcp.gke_configure_k8s(
            ctx, service_account, cluster, is_public, support_runs
        )

    click.echo("Summary of optional feature support:")
    tabulate_rows(
        [[k, v] for k, v in supported_features.items()], headers=["Feature", "Is Enabled"]
    )
    if not is_public:
        click.echo(
            "To enable TLS on a private cluster, supply a trusted TLS certificate to "
            + "`spell kube-cluster set-tls-cert`"
        )

    cluster_utils.echo_delimiter()
    grafana_password = cluster_utils.prompt_grafana_password()
    cluster_utils.update_grafana_configuration(cluster, grafana_password)

    cluster_utils.echo_delimiter()
    with api_client_exception_handler():
        status_code = spell_client.register_serving_cluster(
            cluster["name"],
            SERVING_CLUSTER_VERSION,
            is_public=is_public,
            support_runs=support_runs,
            kube_config=kubecfg_yaml,
            default_ng_config=default_ng_config,
            serving_cluster_domain=kube_cluster_domain,
            serving_cluster_name=kube_cluster_name,
            serving_cluster_status="ready",
        )
        if status_code == 202:
            click.echo("please wait a few minutes for DNS entries to propagate.")

    cluster_utils.echo_delimiter()
    cluster_utils.print_grafana_credentials(cluster, grafana_password)

    cluster_utils.echo_delimiter()

    if is_public:
        click.echo("Checking health of TLS ...")
        try:
            kubectl("-n", "ambassador", "get", "secrets/ambassador-certs")
        except Exception:
            logger.warn(
                "Model servers may not be securely reachable over HTTPS for the next 15 minutes."
                + "If this does not self-resolve, please contact Spell"
            )

    click.echo("Cluster setup complete!")


@command(
    name="update",
    short_help="Update an existing GKE/EKS kubernetes cluster in your Spell VPC.",
    help="""Update an existing GKE/EKS kubernetes cluster in your Spell VPC.""",
)
@click.pass_context
@cluster_utils.check_cli_version
@cluster_utils.pass_cluster
@click.option(
    "-p",
    "--profile",
    help="AWS profile to pull credentials from",
)
@click.option(
    "--kube-cluster-name",
    hidden=True,
    default="spell-model-serving",
    help="Name of the GKE/EKS cluster to update",
)
@click.option(
    "-f",
    "--force",
    is_flag=True,
    help="Force a first-time update",
)
@click.option(
    "--support-runs",
    hidden=True,
    is_flag=True,
    help="Configure this K8S cluster to support runs. Currently in development!",
)
@cluster_utils.for_aws(
    require_import("kubernetes", pkg_extras="cluster-aws"),
    require_install("kubectl", "aws-iam-authenticator"),
    cluster_utils.pass_aws_session(perms=["Use kubectl to modify your EKS cluster"]),
)
@cluster_utils.for_gcp(
    require_import("kubernetes", "googleapiclient", pkg_extras="cluster-gcp"),
    require_install("gcloud", "kubectl"),
    cluster_utils.pass_gcp_project_creds,
    cluster_utils.handle_aws_profile_flag,
)
def update_kube_cluster(
    ctx,
    cluster,
    kube_cluster_name,
    force,
    support_runs,
    aws_session=None,
    gcp_project=None,
    gcp_creds=None,
):
    cluster_utils.check_kube_context()  # TODO(waldo): Replace this check with a --kube-context flag + click confirm
    current_version = cluster.get("serving_cluster_version")

    perform_kube_cluster_upgrade(
        ctx,
        cluster,
        kube_cluster_name,
        force,
        support_runs,
        aws_session=aws_session,
        gcp_creds=gcp_creds,
    )
    if current_version and version.parse(current_version) < version.parse("0.10.0"):
        # Generate a random password for grafana
        password = "".join((random.choice(string.ascii_letters + string.digits) for i in range(16)))
        cluster_utils.update_grafana_configuration(cluster, password)
        click.echo(
            "Support has been added for cluster and model server monitoring via Grafana"
            + "-- use `spell kube-cluster get-grafana-password` to get credentials"
        )


def perform_kube_cluster_upgrade(
    ctx,
    cluster,
    kube_cluster_name,
    force,
    support_runs,
    aws_session=None,
    gcp_creds=None,
):
    if not cluster.get("serving_cluster_name"):
        raise ExitException(
            "Model serving is not enabled for this cluster; please run `spell kube-cluster create`."
        )
    current_version = cluster.get("serving_cluster_version")
    if not current_version:
        if not force:
            raise ExitException(
                "This is the first time update-kube-cluster has been run for this serving cluster."
                + " If your cluster was created before 09/16/2020, please upgrade by"
                + " using `delete-kube-cluster` and `create-kube-cluster` instead. Use --force to bypass."
            )
        click.echo(
            "Upgrading serving cluster version to {}. Hang tight!".format(SERVING_CLUSTER_VERSION)
        )
    elif (
        current_version
        and version.parse(current_version).major != version.parse(SERVING_CLUSTER_VERSION).major
    ):
        raise ExitException(
            (
                "This update is a major update (moving from {} to {}). Use `delete-kube-cluster`"
                + " and `create-kube-cluster` to continue."
            ).format(current_version, SERVING_CLUSTER_VERSION)
        )
    elif current_version:
        if not force and not click.confirm(
            "This will upgrade serving cluster version to {}, from {}. Continue?".format(
                SERVING_CLUSTER_VERSION, current_version
            )
        ):
            return

    # Update run-specific infra
    if support_runs:
        cluster_utils.create_namespace("spell-run")
        kube_runs.add_argo()

    # Update infrastructure shared to runs and runs / serving
    if cluster["cloud_provider"] == "AWS":
        eks_update(ctx, aws_session, cluster, kube_cluster_name, support_runs)
    elif cluster["cloud_provider"] == "GCP":
        gke_update(ctx, gcp_creds, cluster, kube_cluster_name, support_runs)
    else:
        raise ExitException("Unsupported cloud provider")

    cluster_utils.finalize_kube_cluster()

    spell_client = ctx.obj["client"]
    click.echo("Sending update notification to Spell...")
    with api_client_exception_handler():
        spell_client.update_serving_cluster(
            cluster["name"],
            SERVING_CLUSTER_VERSION,
            support_runs=support_runs,
        )
    click.echo(f"Successfully updated serving cluster to version {SERVING_CLUSTER_VERSION}!")
    if not current_version:
        logger.warn(
            "If you encounter issues after update, try deleting and recreating your cluster."
        )


@command(
    name="delete",
    help="Delete your EKS/GKE kubernetes cluster",
)
@click.pass_context
@cluster_utils.check_cli_version
@cluster_utils.pass_cluster
@click.option(
    "-p",
    "--profile",
    help="AWS profile to pull credentials from",
)
@cluster_utils.for_aws(
    require_install("eksctl"),
    cluster_utils.pass_aws_session(perms=["Leverage eksctl to delete the model serving cluster"]),
)
@cluster_utils.for_gcp(
    require_install("gcloud"),
    cluster_utils.handle_aws_profile_flag,
)
def delete_kube_cluster(ctx, cluster, aws_session=None):
    serving_cluster_name = cluster.get("serving_cluster_name")
    if not serving_cluster_name:
        click.echo("No serving cluster found, nothing to do!")
        return

    if cluster["cloud_provider"] == "AWS":
        eks_delete_cluster(aws_session.profile_name, serving_cluster_name)
    if cluster["cloud_provider"] == "GCP":
        project_id = cluster["networking"]["gcp"]["project"]
        gke_delete_cluster(project_id, cluster)

    spell_client = ctx.obj["client"]
    with api_client_exception_handler():
        spell_client.deregister_serving_cluster(cluster["name"])
    click.echo("Cluster delete complete!")


@command(
    name="describe",
    help="Get info for this org's serving cluster, if it exists",
)
@click.pass_context
@cluster_utils.check_cli_version
@cluster_utils.pass_cluster
@check_kube_cluster_exists
def describe_kube_cluster(ctx, cluster):
    headers = [
        "Name in Cloud Console",
        "Provider Location",
        "spell.services Domain",
        "Uses Public Subnets?",
        "Version",
    ]

    # TODO(waldo) remove this once serving cluster name is backfilled
    serving_cluster_name = cluster.get("serving_cluster_short_name")
    if not serving_cluster_name:
        serving_cluster_name = cluster.get("serving_cluster_name")

    # NOTE(waldo) On older clusters, some of these fields may be empty
    # since old versions of the CLI don't send these fields to the API during setup
    info = [
        [
            serving_cluster_name,
            cluster.get("serving_cluster_location"),
            cluster.get("serving_cluster_domain"),
            cluster.get("is_serving_cluster_public"),
            cluster.get("serving_cluster_version"),
        ]
    ]
    click.echo(tabulate_rows(info, headers))


@command(
    name="set-tls-cert",
    help="Use a custom TLS certificate to enable TLS to model servers within a private cluster",
)
@click.option("--cert-path", help="Path to certificate file", required=True)
@click.option("--key-path", help="Path to key file for certificate", required=True)
@click.pass_context
@cluster_utils.check_cli_version
@cluster_utils.pass_cluster
@check_kube_cluster_exists
def swap_ambassador_cert(ctx, cluster, cert_path, key_path):
    if cluster.get("serving_cluster_is_public"):
        raise ExitException(
            "Public clusters use TLS certs provisioned from LetsEncrypt, certs do not need to be swapped"
        )

    try:
        cluster_utils.kubectl(
            "delete", "secret", "-n", "ambassador", "ambassador-certs", "--ignore-not-found"
        )
        cluster_utils.kubectl(
            "create",
            "secret",
            "tls",
            "-n",
            "ambassador",
            "ambassador-certs",
            "--cert",
            cert_path,
            "--key",
            key_path,
        )
    except Exception as e:
        raise ExitException(f"Failed to swap TLS cert: {e}")
    click.echo("TLS cert swapped!")


@command(
    name="get-grafana-password",
    help="Get Grafana password as plaintext (must be Manager/Admin)",
)
@click.pass_context
@cluster_utils.pass_cluster
def get_grafana_password(ctx, cluster):
    spell_client = ctx.obj["client"]
    with api_client_exception_handler():
        password = spell_client.get_grafana_password(cluster["name"])
    click.echo(password)


@command(
    name="reset-grafana-password",
    help="Reset Grafana Password (must have kubectl access to serving cluster)",
)
@click.pass_context
@cluster_utils.check_cli_version
@cluster_utils.pass_cluster
def reset_grafana_password(ctx, cluster):
    cluster_utils.check_kube_context()
    grafana_password = cluster_utils.prompt_grafana_password()
    cluster_utils.update_grafana_configuration(cluster, grafana_password)
    cluster_utils.print_grafana_credentials(cluster, grafana_password)


@command(
    name="add-user",
    help="Grant another AWS User in your account permissions to manage your kube cluster. "
    "These permissions are required for anyone to update the cluster or create/remove node groups. "
    "The user must be in the same account you use to manage this cluster, "
    "which we will deduce from the AWS profile you provide (you will be prompted to confirm).",
)
@click.pass_context
@click.argument("user")
@cluster_utils.check_cli_version
@cluster_utils.pass_cluster
@click.option("-p", "--profile", help="AWS profile to pull credentials from")
@cluster_utils.for_aws(
    require_install("eksctl"),
    cluster_utils.pass_aws_session(
        perms=["Leverage eksctl to grant an AWS IAM User kube admin privileges"]
    ),
)
def kube_cluster_add_user(ctx, user, cluster, aws_session=None):
    if cluster["cloud_provider"] == "GCP":
        raise ExitException("This command is only intended for AWS")
    if not cluster.get("serving_cluster_name"):
        raise ExitException(
            "No kube cluster found. You can run 'spell kube-cluster create' to make one"
        )

    sts = aws_session.client("sts")
    identity = sts.get_caller_identity()
    account_id = identity.get("Account")
    if not account_id:
        raise ExitException("Unable to determine your AWS account from your profile")
    if not click.confirm(
        "Grant user {} from account {} the ability to manage your kube cluster?".format(
            user, account_id
        )
    ):
        return

    arn = "arn:aws:iam::{}:user/{}".format(account_id, user)
    eks_add_arn(aws_session.profile_name, cluster, arn)

    click.echo("{} added!".format(user))


# Node-groups
@click.group(
    name="node-group",
    short_help="Manage kube cluster node groups",
    help="Manage node groups used for model serving cluster nodes",
)
@click.pass_context
@cluster_utils.pass_cluster
def node_group(ctx, cluster):
    pass


@click.command(name="list", short_help="Display all your node groups")
@docs_option("https://spell.ml/docs/serving_clusters/#listing-node-groups")
@click.pass_context
@cluster_utils.check_cli_version
@cluster_utils.pass_cluster
def node_group_list(ctx, cluster):
    spell_client = ctx.obj["client"]
    with api_client_exception_handler():
        node_groups = spell_client.get_node_groups(cluster["name"])
    if node_groups:

        def prettify_instance_type(instance_type, accels, is_spot):
            type_str = instance_type or "Custom"
            accels_str = ""
            if accels:
                accel_strs = []
                for accel in accels:
                    accel_type = accel["type"]
                    # GCP accelerator types start with "nvidia-tesla-" so we can trim the prefix
                    if accel_type.startswith("nvidia-tesla-"):
                        accel_type = accel_type[len("nvidia-tesla-") :]
                    accel_strs.append("{}x{}".format(accel_type, accel["count"]))
                accels_str = "+" + ",".join(accel_strs)
            cluster_spot_name = "preemptible" if cluster["cloud_provider"] == "GCP" else "spot"
            spot_str = " ({})".format(cluster_spot_name) if is_spot else ""
            return "{}{}{}".format(type_str, accels_str, spot_str)

        tabulate_rows(
            [
                (
                    sg["name"],
                    prettify_instance_type(sg["instance_type"], sg["accelerators"], sg["is_spot"]),
                    sg["disk_size_gb"],
                    sg["min_nodes"],
                    sg["max_nodes"],
                )
                for sg in node_groups
            ],
            headers=["NAME", "INSTANCE TYPE", "DISK SIZE", "MIN NODES", "MAX NODES"],
        )
    else:
        click.echo("No node groups found for cluster {}".format(cluster["name"]))


@click.command(name="add", short_help="Add a new node group to a Spell model serving cluster")
@click.pass_context
@cluster_utils.check_cli_version
@cluster_utils.pass_cluster
@click.option(
    "-p",
    "--profile",
    help="Specify an AWS profile to pull credentials from to perform the NodeGroup create operation",
)
@click.option(
    "--name",
    required=True,
    help="Name of the node group",
)
@click.option(
    "--instance-type",
    help="Instance type to use for the nodes",
)
@click.option(
    "--accelerator",
    "accelerators",
    multiple=True,
    metavar="NAME[:COUNT]",
    help="(GCP only) Accelerator to attach to nodes, can be specified multiple times for multiple accelerator types",
)
@click.option(
    "--min-nodes",
    type=int,
    help="Minimum number of autoscaled nodes in the node group",
)
@click.option(
    "--max-nodes",
    type=int,
    help="Maximum number of autoscaled nodes in the node group",
)
@click.option(
    "--spot",
    is_flag=True,
    default=None,
    help="Use spot instances for node group nodes",
)
@click.option(
    "--disk-size",
    type=int,
    help="Size of disks on each node in GB",
)
@click.option(
    "--config-file",
    type=click.Path(exists=True, dir_okay=False),
    help="Path to file containing eksctl NodeGroup or GKE node pool spec. Note this is "
    "an advanced option for users who want to specify a custom node group or node pool configuration.",
)
@cluster_utils.for_aws(
    cluster_utils.pass_aws_session(
        perms=["Leverage eksctl to create a new autoscaling group to back the node group"],
    ),
)
@cluster_utils.for_gcp(
    require_import("googleapiclient.discovery", pkg_extras="cluster-gcp"),
    cluster_utils.pass_gcp_project_creds,
    cluster_utils.handle_aws_profile_flag,
)
@docs_option("https://spell.ml/docs/serving_clusters/#creating-node-groups")
def node_group_add(
    ctx,
    cluster,
    name,
    instance_type,
    accelerators,
    min_nodes,
    max_nodes,
    spot,
    disk_size,
    config_file,
    aws_session=None,
    gcp_project=None,
    gcp_creds=None,
):
    """
    Deploy a GKE node pool or eksctl node group for model serving
    """
    spell_client = ctx.obj["client"]

    accel_configs = ",".join(accelerators)

    config_contents = None
    if config_file:
        with open(config_file) as f:
            config_contents = f.read()

    cluster_utils.validate_org_perms(spell_client, ctx.obj["owner"])

    if config_contents is None:
        click.echo("Retrieving config...")
        with api_client_exception_handler():
            config = spell_client.generate_node_group_config(
                cluster["name"],
                name,
                instance_type,
                accel_configs,
                min_nodes,
                max_nodes,
                spot,
                disk_size,
            )

    if cluster["cloud_provider"] == "AWS":
        cluster_aws.eks_check_node_group_perms(cluster, aws_session, "create")
        cluster_aws.eks_add_nodegroup(name, config, aws_session.profile_name)
    elif cluster["cloud_provider"] == "GCP":
        # External cluster service acct credentials given to nodes in the new node group
        gcp_service_account = cluster["role_credentials"]["gcp"]["service_account_id"]
        gke_add_nodepool(name, config, gcp_service_account, gcp_creds)
    else:
        raise ExitException("Cluster has invalid provider {}".format(cluster["cloud_provider"]))

    with api_client_exception_handler():
        spell_client.create_node_group(cluster["name"], name, config)
    click.echo("Successfully created node group {}!".format(name))


@click.command(
    name="scale",
    short_help="Adjust minimum and maximum node counts for a given node group",
)
@click.pass_context
@cluster_utils.check_cli_version
@cluster_utils.pass_cluster
@click.option(
    "-p",
    "--profile",
    help="Specify an AWS profile to pull credentials from to perform the NodeGroup scale operation",
)
@click.option(
    "--min-nodes",
    type=int,
    help="Minimum number of autoscaled nodes in the node group",
)
@click.option(
    "--max-nodes",
    type=int,
    help="Maximum number of autoscaled nodes in the node group",
)
@click.argument("node_group_name")
@cluster_utils.for_gcp(
    require_import("googleapiclient.discovery", pkg_extras="cluster-gcp"),
    cluster_utils.pass_gcp_project_creds,
    cluster_utils.handle_aws_profile_flag,
)
@cluster_utils.for_aws(
    require_install("eksctl"),
    cluster_utils.pass_aws_session(
        perms=[
            "Retrieve the EC2 autoscaling group corresponding to the node group",
            "Adjust the MinSize and MaxSize of the autoscaling group",
        ],
    ),
)
@docs_option("https://spell.ml/docs/serving_clusters/#scaling-node-groups")
def node_group_scale(
    ctx,
    cluster,
    node_group_name,
    min_nodes,
    max_nodes,
    aws_session=None,
    gcp_project=None,
    gcp_creds=None,
):
    """
    Adjust autoscaling min/max nodes for a node group
    """
    if min_nodes is None and max_nodes is None:
        raise click.UsageError("One of --min-nodes or --max-nodes must be specified")

    spell_client = ctx.obj["client"]
    with api_client_exception_handler():
        node_group = spell_client.get_node_group(cluster["name"], node_group_name)

    if node_group.is_default and max_nodes is not None and max_nodes < 1:
        raise ExitException(
            'Cannot scale default node group "{}" to below 1 node'.format(node_group_name)
        )

    min_nodes = node_group.min_nodes if min_nodes is None else min_nodes
    max_nodes = node_group.max_nodes if max_nodes is None else max_nodes
    if cluster["cloud_provider"] == "AWS":
        cluster_aws.eks_check_node_group_perms(cluster, aws_session, "scale")
        cluster_aws.eks_scale_nodegroup(aws_session, cluster, node_group_name, min_nodes, max_nodes)
    elif cluster["cloud_provider"] == "GCP":
        gke_scale_nodepool(gcp_creds, node_group, min_nodes, max_nodes)
    else:
        raise ExitException("Cluster has invalid provider {}".format(cluster["cloud_provider"]))

    with api_client_exception_handler():
        spell_client.scale_node_group(cluster["name"], node_group_name, min_nodes, max_nodes)
    click.echo("Successfully scaled node group {}!".format(node_group_name))


@click.command(
    name="delete",
    short_help="Delete a node group",
)
@click.pass_context
@cluster_utils.check_cli_version
@cluster_utils.pass_cluster
@click.option(
    "-p",
    "--profile",
    help="AWS profile to pull credentials from",
)
@click.argument("node_group_name")
@cluster_utils.for_aws(
    require_install("eksctl"),
    cluster_utils.pass_aws_session(
        perms=["Leverage eksctl to delete the autoscaling group backing the node group"],
    ),
)
@cluster_utils.for_gcp(
    require_import("googleapiclient.discovery", pkg_extras="cluster-gcp"),
    cluster_utils.pass_gcp_project_creds,
    cluster_utils.handle_aws_profile_flag,
)
@docs_option("https://spell.ml/docs/serving_clusters/#deleting-node-groups")
def node_group_delete(
    ctx,
    cluster,
    node_group_name,
    aws_session=None,
    gcp_project=None,
    gcp_creds=None,
):
    """
    Delete a node group
    """
    spell_client = ctx.obj["client"]

    cluster_utils.validate_org_perms(spell_client, ctx.obj["owner"])

    with api_client_exception_handler():
        node_group = spell_client.get_node_group(cluster["name"], node_group_name)

    if node_group.is_default:
        raise ExitException('Cannot delete cluster default node group "{}"'.format(node_group_name))

    active_servers = [
        server
        for server in node_group.model_servers
        if server.status in ["running", "starting", "updating"]
    ]

    if len(active_servers) > 0:
        server_names = [server.server_name for server in active_servers]
        if not click.confirm(
            "These active model servers will be stopped: ({}). Are you sure?".format(
                ", ".join(server_names)
            )
        ):
            click.echo("Aborted.")
            return
        for model_server in active_servers:
            spell_client.stop_model_server(model_server.server_name)

    if cluster["cloud_provider"] == "AWS":
        cluster_aws.eks_check_node_group_perms(cluster, aws_session, "delete")
        cluster_aws.eks_delete_nodegroup(aws_session.profile_name, node_group)
    elif cluster["cloud_provider"] == "GCP":
        gke_delete_nodepool(gcp_creds, node_group)
    else:
        raise ExitException("Cluster has invalid provider {}".format(cluster["cloud_provider"]))

    with api_client_exception_handler():
        spell_client.delete_node_group(cluster["name"], node_group_name)
    click.echo("Successfully deleted node group {}!".format(node_group_name)),


kube_cluster.add_command(create_kube_cluster)
kube_cluster.add_command(update_kube_cluster)
kube_cluster.add_command(delete_kube_cluster)
kube_cluster.add_command(kube_cluster_add_user)
kube_cluster.add_command(describe_kube_cluster)
kube_cluster.add_command(swap_ambassador_cert)
kube_cluster.add_command(get_grafana_password)
kube_cluster.add_command(reset_grafana_password)
kube_cluster.add_command(kubectl)

kube_cluster.add_command(node_group)
node_group.add_command(node_group_list)
node_group.add_command(node_group_add)
node_group.add_command(node_group_scale)
node_group.add_command(node_group_delete)
