from typing import Any, Callable, Generic, List, Type, TypeVar

from fastapi import APIRouter
from pydantic import BaseModel
from starlette import status

from .json_api import JsonApiSuccessResponse

T = TypeVar("T", bound=BaseModel)  # noqa: WPS111


class CRUDGenerator(Generic[T], APIRouter):  # noqa: WPS214
    schema: Type[T]
    create_schema: Type[T]
    _base_path: str = "/"

    def __init__(self, schema: Type[T], create_schema: Type[T], **kwargs: Any) -> None:

        self.schema = schema
        self.create_schema = create_schema

        schema_name = self.schema.__name__

        prefix = "{path}{schema}s".format(
            path=self._base_path, schema=self.schema.__name__.lower().strip("/"),
        )
        tags = [prefix.strip("/")]

        super().__init__(prefix=prefix, tags=tags, **kwargs)  # noqa: WPS613

        self._add_api_route(
            "",
            self._create(),
            methods=["POST"],
            name="{0}s:create_{0}".format(schema_name),
            summary="Creates a new {0}".format(schema_name),
            status_code=status.HTTP_201_CREATED,
            response_model=JsonApiSuccessResponse[self.create_schema],
        )

        self._add_api_route(
            "/{entity_id}",
            self._read(),
            methods=["GET"],
            name="{0}s:get_{0}".format(schema_name),
            summary="Gets an existing {0} by id".format(schema_name),
            status_code=status.HTTP_200_OK,
            response_model=JsonApiSuccessResponse[self.schema],
        )

        self._add_api_route(
            "",
            self._read_all(),
            methods=["GET"],
            name="{0}s:get_all".format(schema_name),
            summary="Gets all existing {0} entities in the system".format(schema_name),
            status_code=status.HTTP_200_OK,
            response_model=JsonApiSuccessResponse[List[self.schema]],
            response_model_exclude_unset=True,
        )

        self._add_api_route(
            "/{entity_id}",
            self._update(),
            methods=["PATCH"],
            name="{0}s:update_{0}".format(schema_name),
            summary="Updates an existing {0}".format(schema_name),
            status_code=status.HTTP_200_OK,
            response_model=JsonApiSuccessResponse[self.create_schema],
        )

        self._add_api_route(
            "/{entity_id}",
            self._delete(),
            methods=["DELETE"],
            name="{0}s:delete_{0}".format(schema_name),
            summary="Deletes an existing {0}".format(schema_name),
            status_code=status.HTTP_204_NO_CONTENT,
        )

        self._add_api_route(
            "",
            self._delete_all(),
            methods=["DELETE"],
            name="{0}s:delete_all".format(schema_name),
            summary="Deletes all existing {0} entities in the system".format(
                schema_name,
            ),
            status_code=status.HTTP_204_NO_CONTENT,
        )

    def _add_api_route(
        self, path: str, endpoint: Callable[..., Any], **kwargs: Any,
    ) -> None:
        super().add_api_route(path, endpoint, **kwargs)  # noqa: WPS613

    # These should be overriden by whatever is extending this class.
    def _create(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        raise NotImplementedError

    def _read(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        raise NotImplementedError

    def _read_all(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        raise NotImplementedError

    def _update(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        raise NotImplementedError

    def _delete(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        raise NotImplementedError

    def _delete_all(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        raise NotImplementedError
