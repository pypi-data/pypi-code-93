from enum import Enum

from biolib.typing_utils import TypedDict, List, Optional, Dict, Literal
from biolib.biolib_api_client.common_types import SemanticVersion


class AppVersionSlim(SemanticVersion):
    created_at: str
    public_id: str


class AppVersion(AppVersionSlim):
    app: str
    description: str
    is_runnable_by_user: bool
    source_code_license: str


class App(TypedDict):
    account_display_name: str
    account_handle: str
    account_id: str
    account_profile_picture: str
    active_version: AppVersion
    allow_client_side_execution: bool
    app_versions: List[AppVersionSlim]
    created_at: str
    is_editable_by_user: bool
    is_license_required: bool
    is_open_source: bool
    name: str
    public_id: str


class StdoutRenderType(Enum):
    MARKDOWN = 'markdown'
    TEXT = 'text'


class RemoteHost(TypedDict):
    hostname: str


class ModuleEnvironment(Enum):
    BIOLIB_APP = 'biolib-app'
    BIOLIB_CUSTOM = 'biolib-custom'
    BIOLIB_ECR = 'biolib-ecr'


class FilesMapping(TypedDict):
    from_path: str
    to_path: str


class LargeFileSystemMapping(TypedDict):
    public_id: str
    to_path: str


class Module(TypedDict):
    command: str
    environment: Literal['biolib-app', 'biolib-custom', 'biolib-ecr']
    image_uri: str
    input_files_mappings: List[FilesMapping]
    large_file_systems: List[LargeFileSystemMapping]
    name: str
    output_files_mappings: List[FilesMapping]
    source_files_mappings: List[FilesMapping]
    working_directory: str


class _AppVersionOnJob(TypedDict):
    client_side_executable_zip: Optional[str]
    consumes_stdin: bool
    is_runnable_by_user: bool
    public_id: str
    remote_hosts: List[RemoteHost]
    settings: List[Dict]
    stdout_render_type: Literal['text', 'markdown']


# type optional keys with total=False
class AppVersionOnJob(_AppVersionOnJob, total=False):
    modules: List[Module]
