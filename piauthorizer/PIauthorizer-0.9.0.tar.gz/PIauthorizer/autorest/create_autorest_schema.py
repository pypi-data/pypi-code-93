
import json

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


def create_autorest_schema(app: FastAPI) -> None:
    """creates an openapi.json file for AutoRest schema

    Args:
        app (FastAPI): a FastAPI application
    """
    with open("openapi.json", "w") as f:
        json.dump(
            get_openapi(
                title=app.title,
                version=app.version,
                openapi_version=app.openapi_version,
                description=app.description,
                routes=app.routes,
            ),
            f,
        )
