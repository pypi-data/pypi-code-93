from typing import Any, Callable, Coroutine, Dict, List, Type

from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from loguru import logger
from pydantic import BaseModel
from tinydb import TinyDB

from . import CRUDGenerator
from ..tinydb import crud
from ..json_api import JsonApiRequestEntity

CALLABLE = Callable[..., Coroutine[Any, Any, Dict[str, Any]]]
CALLABLE_LIST = Callable[..., Coroutine[Any, Any, List[Dict[str, Any]]]]  # noqa: WPS221


class TinydbCRUDRouter(CRUDGenerator[BaseModel]):
    def __init__(
        self,
        db: "TinyDB",
        schema: Type[BaseModel],
        create_schema: Type[BaseModel],
        **kwargs: Any,
    ) -> None:

        self.schema_name = schema.__name__
        self.db_func = db

        super().__init__(
            schema=schema, create_schema=create_schema, **kwargs,
        )

    def _create(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            entity: JsonApiRequestEntity[self.create_schema],
            db: TinyDB = Depends(self.db_func),
        ) -> Dict[str, Any]:
            entity = crud.create(db, jsonable_encoder(entity.data))
            logger.info("Created {0} {1}".format(self.schema_name, entity["id"]))
            return {"data": entity}

        return route

    def _read(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            entity_id: str, db: TinyDB = Depends(self.db_func),
        ) -> Dict[str, Any]:
            entity = crud.read(db, entity_id)
            logger.info("Read {0} {1}".format(self.schema_name, entity_id))
            return {"data": entity}

        return route

    def _read_all(self, *args: Any, **kwargs: Any) -> CALLABLE_LIST:
        async def route(
            db: TinyDB = Depends(self.db_func),
        ) -> Dict[str, List[Dict[str, Any]]]:
            entities = crud.read_all(db)
            logger.info("Read all {0}s".format(self.schema_name))
            return {"data": entities}

        return route

    def _update(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            entity_id: str,
            entity: JsonApiRequestEntity[self.create_schema],
            db: TinyDB = Depends(self.db_func),
        ) -> Dict[str, Any]:
            entity = crud.update(db, entity_id, jsonable_encoder(entity.data))
            logger.info("Updated {0} {1}".format(self.schema_name, entity_id))
            return {"data": entity}

        return route

    def _delete(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(entity_id: str, db: TinyDB = Depends(self.db_func)) -> None:
            crud.delete(db, entity_id)
            logger.info("Deleted {0} {1}".format(self.schema_name, entity_id))

        return route

    def _delete_all(self, *args: Any, **kwargs: Any) -> CALLABLE_LIST:
        async def route(db: TinyDB = Depends(self.db_func)) -> None:
            crud.delete_all(db)
            logger.info("Deleted all {0}s".format(self.schema_name))

        return route
