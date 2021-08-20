import uuid
from datetime import datetime
from typing import Any, Dict, List

from fastapi.exceptions import HTTPException
from starlette import status
from tinydb import Query, TinyDB

NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found",
)

query = Query()


def create(db: TinyDB, entity: Dict[str, Any]) -> Dict[str, Any]:
    entity["id"] = str(uuid.uuid4())
    entity["createdTime"] = datetime.now().timestamp()
    entity["updatedTime"] = entity["createdTime"]

    db.insert(entity)
    return entity


def read(db: TinyDB, id: str) -> Dict[str, Any]:
    matching_entities = db.search(query.id == id)

    if not matching_entities:
        raise NOT_FOUND

    return matching_entities[0]


def read_all(db: TinyDB) -> List[Dict[str, Any]]:
    return db.all()


def update(db: TinyDB, id: str, entity: Dict[str, Any]) -> Dict[str, Any]:
    matching_entity = read(db, id)

    entity["id"] = id
    entity["createdTime"] = matching_entity["createdTime"]
    entity["updatedTime"] = datetime.now().timestamp()

    db.update(entity, query.id == id)
    return entity


def delete(db: TinyDB, id: str) -> None:
    read(db, id)
    db.remove(query.id == id)


def delete_all(db: TinyDB) -> None:
    db.drop_tables()
