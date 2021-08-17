from os import getenv
from urllib.parse import urlparse

import boto3
from aws_requests_auth.aws_auth import AWSRequestsAuth
from requests_toolbelt.sessions import BaseUrlSession


class AWSSession(BaseUrlSession):
    def __init__(self, base_url=None):
        base_url = base_url or f"https://{getenv('REST_API_DOMAIN')}/"
        domain = urlparse(base_url).netloc
        super().__init__(base_url)

        self.headers = {
            "User-Agent": f'{getenv("SERVICE", getenv("POWERTOOLS_SERVICE_NAME"))}/{getenv("VERSION", "local")}'
        }
        self.auth = self._get_auth(domain)

    def _get_auth(self, domain):
        session = boto3.session.Session()
        credentials = session.get_credentials().get_frozen_credentials()

        return AWSRequestsAuth(
            aws_access_key=credentials.access_key,
            aws_secret_access_key=credentials.secret_key,
            aws_token=credentials.token,
            aws_host=domain,
            aws_service="execute-api",
            aws_region=session.region_name,
        )
