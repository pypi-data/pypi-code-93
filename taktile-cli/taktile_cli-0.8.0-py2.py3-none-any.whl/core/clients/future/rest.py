import typing as t

from tktl.core.clients.future.http import API
from tktl.core.clients.future.taktile import DeploymentApiClient
from tktl.core.clients.http_client import interpret_response
from tktl.core.future.t import EndpointKinds, ProfileKinds
from tktl.core.loggers import LOG
from tktl.core.schemas.future.service import (
    EndpointInfoSchema,
    InfoEndpointResponseModel,
)
from tktl.core.schemas.repository import RepositoryDeployment, _format_http_url

from .endpoint import RestEndpoints


class RestClient:

    endpoints: RestEndpoints

    def __init__(
        self,
        api_key: str,
        repository_name: str,
        branch_name: str,
        url: t.Optional[str] = None,
    ):
        self._api_key = api_key
        self._repository_name = repository_name
        self._branch_name = branch_name
        self._url = RestClient.__get_url(
            url=url,
            repository_name=repository_name,
            branch_name=branch_name,
            api_key=api_key,
        )

        self._client = RestClient.__get_deployment_client(
            url=self._url, api_key=api_key
        )

        self._info = self.__get_info(api_key=api_key, client=self._client)

        self.endpoints = RestEndpoints(api=self._client, infos=self._info.endpoints)

    @staticmethod
    def __get_deployment(
        *, repository_name: str, branch_name: str, client: DeploymentApiClient
    ) -> RepositoryDeployment:
        return client.get_deployment_by_branch_name(
            repository_name=repository_name, branch_name=branch_name
        )

    @staticmethod
    def __get_info(*, api_key: str, client: API) -> InfoEndpointResponseModel:
        response = client.get("/info")
        response.raise_for_status()

        response_content = response.json()

        if "schema_version" not in response_content:

            # Support for classic deployments
            # TODO: Delete this in taktile-cli 1.0
            LOG.warning("Using compatibility mode for classic deployments...")

            to_profile_kind: t.Dict[str, ProfileKinds] = {
                "binary": ProfileKinds.BINARY,
                "regression": ProfileKinds.REGRESSION,
            }

            def to_kind(endpoint: t.Dict[str, t.Any]) -> EndpointKinds:
                if endpoint["kind"] in ["binary", "regression"]:
                    return EndpointKinds.PROFILED
                if endpoint["kind"] in ["custom"]:
                    return EndpointKinds.ADVANCED
                return EndpointKinds.ADVANCED

            return InfoEndpointResponseModel(
                schema_version="unknown",
                taktile_cli="unknown",
                profiling="unknown",
                endpoints=[
                    EndpointInfoSchema(
                        name=x["name"],
                        path=f"/model/{x['name']}",
                        kind=to_kind(x),
                        profile_kind=to_profile_kind.get(x["kind"], None),
                        explain_path=f"/model/{x['name']}/explain",
                        response_kind=None,
                        input_names=x["input_names"],
                        output_names=x["output_names"] if x["output_names"] else None,
                        profile_columns=x["profiling_columns"],
                        input_example=x["explain_input_example"],
                    )
                    for x in response_content
                ],
            )

        return interpret_response(response, InfoEndpointResponseModel)

    @staticmethod
    def __get_dapi_client(*, api_key: str) -> DeploymentApiClient:
        return DeploymentApiClient(api_key=api_key)

    @staticmethod
    def __get_deployment_client(*, url: str, api_key: str) -> API:
        client = API(api_url=url, headers={"X-Api-Key": api_key})

        return client

    @staticmethod
    def __get_url(
        *, url: t.Optional[str], repository_name: str, branch_name: str, api_key: str
    ) -> str:
        if url:
            return url

        client = RestClient.__get_dapi_client(api_key=api_key)
        deployment = RestClient.__get_deployment(
            repository_name=repository_name, branch_name=branch_name, client=client
        )

        return _format_http_url(deployment.public_docs_url, docs=False)
