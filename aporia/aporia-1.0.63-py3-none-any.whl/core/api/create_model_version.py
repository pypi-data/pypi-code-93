import logging
from typing import Dict, List, Optional

from aporia.core.errors import AporiaError
from aporia.core.graphql_client import GraphQLClient
from aporia.core.logging_utils import LOGGER_NAME
from aporia.core.types.field import FieldCategory, FieldType

VALID_FIELD_TYPES = [field_type.value for field_type in FieldType]

logger = logging.getLogger(LOGGER_NAME)


async def run_create_model_version_query(
    graphql_client: GraphQLClient,
    model_id: str,
    model_version: str,
    model_type: str,
    features: Dict[str, str],
    predictions: Dict[str, str],
    raw_inputs: Optional[Dict[str, str]] = None,
    metrics: Optional[Dict[str, str]] = None,
):
    """Defines the schema for a specific model version.

    Args:
        graphql_client (GraphQLClient): GraphQL client
        model_id (str): Model ID
        model_version (str): Model Version
        model_type (str): Model type
        features (Dict[str, str]): Feature fields
        predictions (Dict[str, str]): Prediction fields
        raw_inputs (Dict[str, str], optional): Raw input fields. Defaults to None.
        metrics (Dict[str, str], optional): Prediction metric fields. Defaults to None.
    """
    query = """
        mutation CreateModelVersion(
            $modelId: String!,
            $modelVersion: String!,
            $modelType: String!,
            $features: [Field]!,
            $predictions: [Field]!,
            $rawInputs: [Field],
            $metrics: [Field]
        ) {
            createModelVersion(
                modelId: $modelId,
                modelVersion: $modelVersion,
                modelType: $modelType,
                features: $features,
                predictions: $predictions
                rawInputs: $rawInputs,
                metrics: $metrics
            ) {
                warnings
            }
        }
    """

    variables = {
        "modelId": model_id,
        "modelVersion": model_version,
        "modelType": model_type,
        "features": prepare_fields(features),
        "predictions": prepare_fields(predictions),
        "rawInputs": None if raw_inputs is None else prepare_fields(raw_inputs),
        "metrics": None if metrics is None else prepare_fields(metrics),
    }

    result = await graphql_client.query_with_retries(query, variables)
    for warning in result["createModelVersion"]["warnings"]:
        logger.warning(warning)


def prepare_fields(fields: Dict[str, str]) -> List[Dict[str, str]]:
    """Creates a list of Field GraphQL objects from a fields dict.

    Args:
        fields (Dict[str, str]): Fields dict

    Returns:
        List[Dict[str, str]]: List of GraphQL Field objects.
    """
    return [{"name": field_name, "type": field_type} for field_name, field_type in fields.items()]


def validate_fields_input(
    features: Dict[str, str],
    predictions: Dict[str, str],
    raw_inputs: Optional[Dict[str, str]] = None,
    metrics: Optional[Dict[str, str]] = None,
):
    """Checks if the fields passed to create_model_version are valid.

    Args:
        predictions (Dict[str, str]): Prediction fields
        features (Dict[str, str]): Feature fields
        raw_inputs (Dict[str, str], optional): Raw input fields. Defaults to None.
        metrics (Dict[str, str], optional): Prediction metric fields. Defaults to None.
    """
    fields_to_validate = {FieldCategory.FEATURES: features, FieldCategory.PREDICTIONS: predictions}

    if raw_inputs is not None:
        fields_to_validate[FieldCategory.RAW_INPUTS] = raw_inputs

    if metrics is not None:
        fields_to_validate[FieldCategory.METRICS] = metrics

    for category, fields in fields_to_validate.items():
        if not isinstance(fields, dict):
            raise AporiaError("{} parameter must be a dict".format(category.value))

        if len(fields) == 0:
            raise AporiaError("{} parameter must contain items".format(category.value))

        for key, value in fields.items():
            if not isinstance(key, str):
                raise AporiaError(
                    "Invalid field name {} in the {} parameter - field names must be strings".format(
                        key, category.value
                    )
                )

            if value not in VALID_FIELD_TYPES:
                raise AporiaError(
                    "Invalid field type {} in the {} parameter - valid field types are {}".format(
                        value, category.value, VALID_FIELD_TYPES
                    )
                )
