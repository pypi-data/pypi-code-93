import requests

from biolib.typing_utils import Optional
from biolib.biolib_api_client import RemoteHost
from biolib.compute_node.enclave.parent_api_types import VsockProxyResponse, EnclaveConfig


class ParentApi:
    _BASE_URL = 'http://127.0.0.1:5005'
    _enclave_config: Optional[EnclaveConfig] = None

    @staticmethod
    def get_enclave_config() -> EnclaveConfig:
        if ParentApi._enclave_config:
            return ParentApi._enclave_config

        response = requests.get(f'{ParentApi._BASE_URL}/config/', timeout=5)
        ParentApi._enclave_config = response.json()
        return ParentApi._enclave_config

    @staticmethod
    def deregister_and_shutdown() -> None:
        requests.post(url=f'{ParentApi._BASE_URL}/deregister_and_shutdown/', timeout=5)

    @staticmethod
    def start_vsock_proxy(remote_host: RemoteHost) -> VsockProxyResponse:
        response = requests.post(url=f'{ParentApi._BASE_URL}/vsock_proxy/', json=remote_host, timeout=5)
        vsock_proxy: VsockProxyResponse = response.json()
        return vsock_proxy

    @staticmethod
    def stop_vsock_proxy(vsock_proxy_id: str) -> None:
        requests.delete(url=f'{ParentApi._BASE_URL}/vsock_proxy/{vsock_proxy_id}/', timeout=5)

    @staticmethod
    def start_shutdown_timer(minutes_until_shutdown: int) -> None:
        requests.post(
            url=f'{ParentApi._BASE_URL}/start_shutdown_timer/',
            json={'minutes_until_shutdown': minutes_until_shutdown},
            timeout=5,
        )
