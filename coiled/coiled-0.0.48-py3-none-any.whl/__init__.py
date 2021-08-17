# Get function backing "coiled install" command
from .cli.install import install as _install
from .cluster import Cluster
from .core import (
    Cloud,
    cluster_cost_estimate,
    cluster_logs,
    create_cluster,
    create_cluster_configuration,
    create_job_configuration,
    create_notebook,
    create_software_environment,
    delete_cluster,
    delete_cluster_configuration,
    delete_job_configuration,
    delete_software_environment,
    diagnostics,
    get_notifications,
    get_software_info,
    job_logs,
    list_cluster_configurations,
    list_clusters,
    list_core_usage,
    list_job_configurations,
    list_jobs,
    list_local_versions,
    list_performance_reports,
    list_software_environments,
    list_user_information,
    performance_report,
    set_backend_options,
    start_job,
    stop_job,
)

install = _install.callback
del _install

# Get function backing "coiled upload" command
from .cli.upload import upload as _upload

upload = _upload.callback
del _upload

# Get function backing "coiled env inspect" command
from .cli.env import inspect as _inspect

inspect = _inspect.callback
del _inspect

# Register coiled configuration values with Dask's config system
from . import config

del config

# Top-level coiled.config attribute
def __getattr__(name):
    if name == "config":
        import dask

        return dask.config.get("coiled")
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


# Use versioneer to handle package versioning
from ._version import get_versions

__version__ = get_versions()["version"]
del get_versions

__all__ = [
    "Cloud",
    "Cluster",
    "cluster_cost_estimate",
    "cluster_logs",
    "create_cluster",
    "create_cluster_configuration",
    "create_job_configuration",
    "create_notebook",
    "create_software_environment",
    "delete_cluster",
    "delete_cluster_configuration",
    "delete_job_configuration",
    "delete_software_environment",
    "diagnostics",
    "get_notifications",
    "get_software_info",
    "install",
    "job_logs",
    "list_cluster_configurations",
    "list_clusters",
    "list_core_usage",
    "list_job_configurations",
    "list_jobs",
    "list_local_versions",
    "list_performance_reports",
    "list_software_environments",
    "list_user_information",
    "performance_report",
    "start_job",
    "stop_job",
    "set_backend_options",
]
