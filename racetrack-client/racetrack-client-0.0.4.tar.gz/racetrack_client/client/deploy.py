import dataclasses
import logging
from typing import Optional, Dict
from urllib.parse import urlsplit

import backoff
import requests
import urllib3
from racetrack_client.client_config.client_config import ClientConfig, Credentials
from racetrack_client.client_config.io import load_client_config
from racetrack_client.log.context_error import ContextError
from racetrack_client.manifest import Manifest
from racetrack_client.manifest.validate import load_validated_manifest
from racetrack_client.utils.request import parse_response

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DEPLOYMENT_TIMEOUT_SECS = 10 * 60  # seconds


def send_deploy_request(
    workdir: str,
    manifest: Optional[Manifest] = None,
    client_config: Optional[ClientConfig] = None,
    lifecycle_api_url: Optional[str] = None,
):
    """Send request deploying a new Fatman to running LC instance"""
    if client_config is None:
        client_config = load_client_config()
    if manifest is None:
        manifest = load_validated_manifest(workdir)
        logging.debug(f'Manifest loaded: {manifest}')
    lifecycle_api_url = lifecycle_api_url or client_config.lifecycle_api_url
    logging.info(f'deploying workspace "{workdir}" to {lifecycle_api_url}')

    _handle_local_repository(manifest, lifecycle_api_url)
    git_credentials = get_git_credentials(manifest, client_config)

    # see `lifecycle.server.endpoints::setup_api_endpoints::DeployEndpoint` for server-side implementation
    r = requests.post(
        f'{lifecycle_api_url}/api/v1/deploy',
        json=_get_deploy_request_payload(manifest, git_credentials),
        verify=False,
    )
    response = parse_response(r, 'LC-API deploying error')
    deploy_id = response["id"]
    logging.info(f'job deployment requested: {deploy_id}')

    try:
        fatman_url = _wait_for_deployment_result(lifecycle_api_url, deploy_id)
    except Exception as e:
        raise ContextError('fatman failed to deploy', e)

    logging.info(f'Fatman "{manifest.name}" has been deployed. Check out {fatman_url} to access your fatman')


def _get_deploy_request_payload(manifest: Manifest, git_credentials: Optional[Credentials]) -> Dict:
    return {
        "manifest": dataclasses.asdict(manifest),
        "git_credentials": dataclasses.asdict(git_credentials) if git_credentials is not None else None,
    }


@backoff.on_exception(
    backoff.fibo, TimeoutError, max_value=5, max_time=DEPLOYMENT_TIMEOUT_SECS, jitter=None, logger=None
)
def _wait_for_deployment_result(lifecycle_api_url: str, deploy_id: str) -> str:
    # see `lifecycle.server.endpoints::setup_api_endpoints::DeployIdEndpoint` for server-side implementation
    r = requests.get(
        f'{lifecycle_api_url}/api/v1/deploy/{deploy_id}',
        verify=False,
    )
    response = parse_response(r, 'LC-API deployment status')
    status = response['status'].lower()
    if status == 'failed':
        raise RuntimeError(response['error'])
    if status == 'done':
        return response.get('fatman', {}).get('pub_url')

    logging.info(f'deployment in progress...')
    raise TimeoutError('Deployment timeout error')


def _handle_local_repository(manifest: Manifest, lifecycle_api_url: str):
    """Avoid fetching from GitLab when using samples from local project repository"""
    if manifest.git.remote == 'https://rep.erst.dk/git/kubernilla/ikp-rt' and _is_url_localhost(lifecycle_api_url):
        manifest.git.remote = '.'


def get_git_credentials(manifest: Manifest, client_config: ClientConfig) -> Optional[Credentials]:
    if manifest.git.remote in client_config.git_credentials:
        return client_config.git_credentials[manifest.git.remote]

    split = urlsplit(manifest.git.remote)

    url = f'{split.scheme}://{split.netloc}{split.path}'
    if url in client_config.git_credentials:
        return client_config.git_credentials[url]

    url = f'{split.scheme}://{split.netloc}'
    if url in client_config.git_credentials:
        return client_config.git_credentials[url]

    url = f'{split.netloc}'
    if url in client_config.git_credentials:
        return client_config.git_credentials[url]

    return None


def _is_url_localhost(url: str) -> bool:
    split = urlsplit(url)
    return split.hostname in {'localhost', '127.0.0.1'}
