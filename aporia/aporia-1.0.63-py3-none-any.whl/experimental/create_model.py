from typing import Optional

from aporia.core.context import get_context
from aporia.core.errors import AporiaError, handle_error
from aporia.core.graphql_client import GraphQLClient


def create_model(
    name: str,
    description: Optional[str] = None,
    color: Optional[str] = None,
    icon: Optional[str] = None,
) -> Optional[str]:
    """Create a new model.

    Args:
        name: Model name.
        description: Model description. Defaults to None.
        color: Model color. Must be one of the following(Defaults to blue):
            * blue
            * arctic_blue
            * green
            * turquoise
            * pink
            * purple
            * yellow
            * red
        icon: Model icon. Must be one of the following (Defaults to 'general'):
            * general
            * churn-and-retention
            * conversion-predict
            * anomaly
            * dynamic-pricing
            * email-filtering
            * demand-forecasting
            * ltv
            * personalization
            * fraud-detection
            * credit-risk
            * recommendations

    Notes:
        * This API is experimental and may change in the future.

    Returns:
        Model ID
    """
    context = get_context()

    try:
        if len(name) == 0:
            raise AporiaError("name must be a non-empty string.")

        model_id = context.event_loop.run_coroutine(
            _run_create_model_query(
                graphql_client=context.graphql_client,
                name=name,
                description=description,
                color=color,
                icon=icon,
            )
        )

        return model_id
    except Exception as err:
        handle_error(
            message_format="Creating model failed, error: {}",
            verbose=context.config.verbose,
            throw_errors=context.config.throw_errors,
            debug=context.config.debug,
            original_exception=err,
        )

        return None


async def _run_create_model_query(
    graphql_client: GraphQLClient,
    name: str,
    description: Optional[str] = None,
    color: Optional[str] = None,
    icon: Optional[str] = None,
) -> str:
    query = """
        mutation ExperimentalCreateModel(
            $name: String!,
            $description: String,
            $color: String,
            $icon: String
        ) {
            experimentalCreateModel(
                name: $name,
                description: $description,
                color: $color,
                icon: $icon
            ) {
                modelId
            }
        }
    """

    variables = {
        "name": name,
        "description": description,
        "color": color,
        "icon": icon,
    }

    result = await graphql_client.query_with_retries(query, variables)

    return result["experimentalCreateModel"]["modelId"]
