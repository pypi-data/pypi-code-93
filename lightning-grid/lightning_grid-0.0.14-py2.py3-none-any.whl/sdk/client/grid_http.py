from functools import lru_cache
from typing import List, Optional

import requests
from requests.adapters import HTTPAdapter
from requests_toolbelt import sessions

from grid.metadata import __version__
from grid.sdk.auth import Credentials


@lru_cache(maxsize=None)
def rest_session(url: str, creds: Credentials) -> sessions.BaseUrlSession:
    sess = sessions.BaseUrlSession(base_url=url)
    sess.auth = (creds.user_id, creds.api_key)
    sess.headers = {'Content-type': 'application/json', 'User-Agent': f'grid-api-{__version__}'}
    retries_adaptor = HTTPAdapter(max_retries=3)
    sess.mount(url, retries_adaptor)
    return sess


def list_experiments(sess: sessions.BaseUrlSession, params: Optional[dict] = None) -> List[dict]:
    if params is None:
        params = {}
    resp = sess.get(f'/v1/core/experiments', params=params, timeout=1.0)
    resp.raise_for_status()
    return resp.json()['experiment']


def get_experiment(sess: sessions.BaseUrlSession, exp_id: str) -> dict:
    resp = sess.get(f'/v1/core/experiments/{exp_id}', timeout=1.0)
    resp.raise_for_status()
    return resp.json()['experiment']


def list_clusters(sess: sessions.BaseUrlSession) -> dict:
    resp = sess.get(f'/v1/core/clusters', timeout=1.0)
    resp.raise_for_status()
    return resp.json()['cluster']


def get_cluster(sess: requests.Session, cluster_id: str) -> dict:
    resp = sess.get(f'/v1/core/clusters/{cluster_id}', timeout=1.0)
    resp.raise_for_status()
    return resp.json()['cluster']
