from docker.models.networks import Network  # type: ignore

from biolib.typing_utils import TypedDict, Callable, Optional, List
from biolib.compute_node.remote_host_proxy import RemoteHostProxy
from biolib.biolib_api_client.app_types import Module
from biolib.biolib_api_client.job_types import Job
from biolib.compute_node.utils import SystemExceptionCodes


class StatusUpdate(TypedDict):
    progress: int
    log_message: str


class RemoteExecuteOptions(TypedDict):
    biolib_base_url: str
    job: Job
    root_job_id: str


SendStatusUpdateType = Callable[[StatusUpdate], None]
SendSystemExceptionType = Callable[[SystemExceptionCodes], None]


class LocalExecutorOptions(TypedDict):
    access_token: str
    biolib_base_url: str
    biolib_containers_pull_token: Optional[str]
    internal_network: Optional[Network]
    job: Job
    module: Module
    remote_host_proxies: List[RemoteHostProxy]
    root_job_id: str
    runtime_zip_bytes: Optional[bytes]  # TODO: replace this with a module_source_serialized
    send_status_update: SendStatusUpdateType
    send_system_exception: SendSystemExceptionType
