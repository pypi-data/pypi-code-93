from enum import Enum
from biolib.typing_utils import TypedDict, Optional, List

from biolib.biolib_api_client.app_types import AppVersionOnJob, RemoteHost


class JobState(Enum):
    AWAITING_INPUT = 'awaiting_input'
    CLIENT_ABORTED = 'client_aborted'
    COMPLETED = 'completed'
    FAILED = 'failed'
    IN_PROGRESS = 'in_progress'


class _Job(TypedDict):
    app_version: AppVersionOnJob
    caller_job: Optional[str]
    created_at: str
    public_id: str
    remote_hosts_with_warning: List[RemoteHost]
    user_id: Optional[str]


# type optional keys with total=False
class Job(_Job, total=False):
    custom_compute_node_url: str


class JobWrapper(TypedDict):
    access_token: str
    BASE_URL: str  # TODO: refactor this to lower case
    biolib_containers_pull_token: Optional[str]
    job: Job
