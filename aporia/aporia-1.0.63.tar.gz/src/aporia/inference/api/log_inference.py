import logging
from typing import List

from aporia.core.graphql_client import GraphQLClient
from aporia.core.logging_utils import LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)


async def log_inference_fragments(
    graphql_client: GraphQLClient,
    model_id: str,
    model_version: str,
    environment: str,
    serialized_fragments: List[dict],
    await_insert: bool,
):
    """Reports a batch of inference fragments.

    Args:
        graphql_client (GraphQLClient): GraphQL client
        model_id (str): Model ID
        model_version (str): Model version
        environment (str): Environment in which aporia is running.
        serialized_fragments (List[dict]): List of serialized fragment dicts.
        await_insert (bool): True if the server should wait for the fragments
            to be stored before responding to the sdk.
    """
    query = """
        mutation LogPredict(
            $modelId: String!,
            $modelVersion: String!,
            $environment: String!,
            $predictions: [Prediction]!
            $isSync: Boolean!
        ) {
            logPredictions(
                modelId: $modelId,
                modelVersion: $modelVersion,
                environment: $environment,
                predictions: $predictions
                isSync: $isSync
            ) {
                warnings
            }
        }
    """

    variables = {
        "modelId": model_id,
        "modelVersion": model_version,
        "environment": environment,
        "predictions": serialized_fragments,
        "isSync": await_insert,
    }

    result = await graphql_client.query_with_retries(query, variables)
    for warning in result["logPredictions"]["warnings"]:
        logger.warning(warning)
