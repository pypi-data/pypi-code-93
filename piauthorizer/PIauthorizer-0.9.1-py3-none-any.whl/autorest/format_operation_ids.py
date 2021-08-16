from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.routing import APIRoute


def format_operation_ids(app: FastAPI) -> None:
    """
    Simplify operation IDs so that generated API clients have simpler function
    names.

    Should be called only after all routes have been added.
    Args:
        app (FastAPI): a FastAPI application
    """
    for route in app.routes:
        if isinstance(route, APIRoute):
            preface_part = "".join(route.tags)
            method_part = ""
            name_part = "".join([part.capitalize()
                                for part in route.name.split("_")])
            new_name = f"{preface_part}_{method_part}{name_part}"
            if new_name[0] == '_':
                new_name = new_name[1:]
            route.operation_id = new_name
            route.summary = new_name
