import logging
from typing import Any

from aporia.core.graphql_client import GraphQLClient
from aporia.core.logging_utils import LOGGER_NAME


logger = logging.getLogger(LOGGER_NAME)


async def log_json(
    graphql_client: GraphQLClient, model_id: str, model_version: str, environment: str, data: Any
):
    """Reports arbitrary data.

    Args:
        graphql_client (GraphQLClient): GraphQL client
        model_id (str): Model ID
        model_version (str): Model version
        environment (str): Environment in which aporia SDK is running
        data (Any): Data to report
    """
    query = """
    mutation LogArbitraryData(
        $modelId: String!,
        $modelVersion: String!,
        $environment: String!,
        $data: GenericScalar!
    ) {
        logArbitraryData(
            modelId: $modelId,
            modelVersion: $modelVersion,
            environment: $environment,
            data: $data
        ) {
            warnings
        }
    }
    """

    variables = {
        "modelId": model_id,
        "modelVersion": model_version,
        "environment": environment,
        "data": data,
    }

    result = await graphql_client.query_with_retries(query, variables)
    for warning in result["logArbitraryData"]["warnings"]:
        logger.warning(warning)
