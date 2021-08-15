from typing import List, Optional, Sequence

import httpx
import requests  # type: ignore
from docker import DockerClient
from requests import HTTPError, exceptions
from yellowbox.containers import SafeContainerCreator, get_ports
from yellowbox.extras.postgresql import PostgreSQLService
from yellowbox.networks import anonymous_network
from yellowbox.retry import RetrySpec
from yellowbox.subclasses import RunMixin, SingleEndpointService
from yellowbox.utils import docker_host_name


class HeksherService(SingleEndpointService, RunMixin):
    def __init__(self, docker_client: DockerClient, postgres_image: str = 'postgres:latest',
                 heksher_image: str = 'biocatchltd/heksher:0.3.0', port: int = 0, *,
                 heksher_startup_context_features: str, **kwargs):
        creator = SafeContainerCreator(docker_client)

        self.postgres_service = PostgreSQLService(docker_client, image=postgres_image, default_db='heksher')

        self.heksher = creator.create_and_pull(
            heksher_image, publish_all_ports=True, ports={80: port}, detach=True, environment={
                'HEKSHER_DB_CONNECTION_STRING': self.postgres_service.container_connection_string("postgres"),
                'HEKSHER_STARTUP_CONTEXT_FEATURES': heksher_startup_context_features,
            }
        )
        self.http_client: Optional[httpx.AsyncClient] = None

        self.network = anonymous_network(docker_client)
        self.postgres_service.connect(self.network, aliases=['postgres'])
        self.network.connect(self.heksher, aliases=['heksher'])
        super().__init__((self.heksher, ), **kwargs)

    def start(self, retry_spec: Optional[RetrySpec] = None):
        self.postgres_service.start()
        super().start()
        retry_spec = retry_spec or RetrySpec(attempts=20)
        retry_spec.retry(
            lambda: requests.get(self.local_url + '/api/health', timeout=3).raise_for_status(),  # type: ignore
            (ConnectionError, HTTPError, exceptions.ConnectionError)
        )
        self.http_client = httpx.AsyncClient(base_url=self.local_url)
        return self

    def stop(self, signal='SIGKILL'):
        self.http_client.aclose()
        # difference in default signal
        self.postgres_service.disconnect(self.network)
        self.network.disconnect(self.heksher)
        self.network.remove()
        self.postgres_service.stop(signal)
        super().stop(signal)

    @property
    def heksher_port(self):
        return get_ports(self.heksher)[80]

    @property
    def local_url(self):
        return f'http://127.0.0.1:{self.heksher_port}'

    @property
    def container_url(self):
        return f'http://{docker_host_name}:{self.heksher_port}'

    @property
    def _single_endpoint(self):
        return self.heksher

    async def get_rules(self, setting_names: Optional[Sequence[str]] = None):
        """
        Args:
            setting_names: the settings names to retrieve the rules for, will retrieve all rules for all settings
            if None
        """
        setting_names = setting_names or await self.get_setting_names()
        request_data = {
            "setting_names": setting_names,
            "context_features_options": "*",
            "include_metadata": True,
        }
        response = await self.http_client.post('/api/v1/rules/query', json=request_data)
        response.raise_for_status()
        result = response.json()
        return result["rules"]

    async def get_setting_names(self) -> List[str]:
        response = await self.http_client.get('/api/v1/settings', params={"include_additional_data": False})
        response.raise_for_status()
        result = response.json()
        return [s['name'] for s in result["settings"]]

    async def clear(self):
        settings_names = await self.get_setting_names()
        rules = await self.get_rules(settings_names)
        rules_ids = [rule["rule_id"] for config_rules in rules.values() for rule in config_rules]
        for rule_id in rules_ids:
            (await self.http_client.delete(f'/api/v1/rules/{rule_id}')).raise_for_status()
        for setting_name in settings_names:
            (await self.http_client.delete(f'/api/v1/settings/{setting_name}')).raise_for_status()
