import logging
import os

import httpx
import yaml

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

logger = logging.getLogger(__name__)
TOKEN_URL = 'http://169.254.169.254/computeMetadata/v1/instance/service-accounts/default/token'


def set_access_token(iam_token=None):
    if not iam_token:
        iam_token = ""
        try:
            resp = httpx.get(TOKEN_URL, headers={'Metadata-Flavor': 'Google'})
            if resp.status_code == 200:
                iam_token = resp.json()["access_token"]
        except (httpx.ConnectError, httpx.ConnectTimeout) as e:
            logger.error("couldn't fetch IAM token: %s", e)
    os.environ["IAM_TOKEN"] = iam_token


def load_yaml(file, safe=False):
    try:
        with open(file, "r") as f:
            return yaml.load(f.read(), Loader)
    except FileNotFoundError:
        if safe:
            return dict()
        else:
            raise


DEFAULT_CONFIG_FILENAME = "yappa.yaml"
