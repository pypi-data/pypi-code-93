# flake8: noqa
import os
import sys
import dataclasses
from . import context
from . import scopes
from . import credentials

from .version import __version__  # noqa

sys.path.append(os.path.dirname(__file__))  # noqa

from .agilicus_api import *  # noqa
from .agilicus_api import exceptions  # noqa
from . import patches  # noqa


ApiClient = patches.patched_api_client()


def GetClient(
    issuer=context.ISSUER_DEFAULT,
    cacert=None,
    client_id="agilicus-builtin-cli",
    agilicus_scopes=scopes.DEFAULT_SCOPES,
    auth_local_webserver=True,
):
    creds = credentials.get_credentials(
        issuer=issuer,
        cacert=cacert,
        client_id=client_id,
        agilicus_scopes=agilicus_scopes,
        auth_local_webserver=auth_local_webserver,
    )

    config = Configuration()
    config.access_token = creds.access_token

    @dataclasses.dataclass
    class api:
        users = UsersApi(ApiClient(config))
        organisations = OrganisationsApi(ApiClient(config))
        policies = PolicyApi(ApiClient(config))
        certificates = CertificatesApi(ApiClient(config))
        applications = ApplicationsApi(ApiClient(config))
        groups = GroupsApi(ApiClient(config))
        connectors = ConnectorsApi(ApiClient(config))
        resouces = ResourcesApi(ApiClient(config))
        catalogues = CataloguesApi(ApiClient(config))
        permissions = PermissionsApi(ApiClient(config))
        audits = AuditsApi(ApiClient(config))
        files = FilesApi(ApiClient(config))
        tokens = TokensApi(ApiClient(config))
        diagnostics = DiagnosticsApi(ApiClient(config))
        metrics = MetricsApi(ApiClient(config))
        challenges = ChallengesApi(ApiClient(config))
        application_services = ApplicationServicesApi(ApiClient(config))
        services = ServicesApi(ApiClient(config))
        issuers = IssuersApi(ApiClient(config))
        messages = MessagesApi(ApiClient(config))

    return api
