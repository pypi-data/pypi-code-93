from biolib.typing_utils import TypedDict


class VsockProxyResponse(TypedDict):
    hostname: str
    id: str
    port: int


class ComputeNodeInfo(TypedDict):
    auth_token: str
    public_id: str
    ip_address: str


class EnclaveConfig(TypedDict):
    base_url: str
    biolib_containers_pull_token: str
    compute_node_info: ComputeNodeInfo
    is_dev: bool
