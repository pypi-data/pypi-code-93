from typing import Dict

from aporia.core.graphql_client import GraphQLClient
from aporia.core.types.field import FieldCategory, FieldType


async def get_model_version(
    graphql_client: GraphQLClient, model_id: str, model_version: str
) -> Dict[FieldCategory, Dict[str, FieldType]]:
    """Fetches model version schema.

    Args:
        graphql_client (GraphQLClient): GraphQL client
        model_id (str): Model ID
        model_version (str): Model version

    Notes:
        * This only fetches field categories that can be used
          when reporting training data (features, predictions, raw_inputs)

    Returns:
        Dict[FieldCategory, Dict[str, FieldType]]: Model version schema
    """
    query = """
        query GetModelVersion(
            $modelId: String!,
            $modelVersion: String!,
        ) {
            modelVersionSchema(
                modelId: $modelId,
                modelVersion: $modelVersion,
            ) {
                features {
                    name
                    type
                }
                predictions {
                    name
                    type
                }
                rawInputs {
                    name
                    type
                }
            }
        }
    """

    variables = {"modelId": model_id, "modelVersion": model_version}

    result = await graphql_client.query_with_retries(query, variables)
    return _build_model_version_schema(result["modelVersionSchema"])


def _build_model_version_schema(
    model_version_data: dict,
) -> Dict[FieldCategory, Dict[str, FieldType]]:
    schema = {}
    for category, fields in model_version_data.items():
        if fields is not None:
            schema[FieldCategory.from_camel_case(category)] = {
                field["name"]: FieldType(field["type"]) for field in fields
            }

    return schema
