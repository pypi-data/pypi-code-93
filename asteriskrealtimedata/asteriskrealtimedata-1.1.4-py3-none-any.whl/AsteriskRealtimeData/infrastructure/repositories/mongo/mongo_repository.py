from AsteriskRealtimeData.domain.search_by_criteria_vo import SearchByCriteriaVo
from pymongo import results
from AsteriskRealtimeData.shared.errors.data_not_found_error import DataNotFound
from AsteriskRealtimeData.domain.update_vo import UpdateVo
from uuid import UUID
from antidote import service, Provide, inject
from pymongo.collection import Collection
from AsteriskRealtimeData.domain.entity import Entity

from AsteriskRealtimeData.infrastructure.repositories.mongo.mongo_connection import MongoConnection
from AsteriskRealtimeData.infrastructure.repositories.repository_interface import Repository


@service(singleton=True)
class MongoRespository(Repository):
    @inject
    def __init__(self, connection: Provide[MongoConnection]) -> None:
        self.connection = connection

    def save(
        self, entity: Entity, identify_field: dict,
    ):
        table = self._get_table()
        return table.replace_one(identify_field, entity.as_dict(), upsert=True,)

    def update(self, update_vo: UpdateVo):
        table = self._get_table()
        a = update_vo.get_key_field()
        b = update_vo.get_update_fields()
        result = table.update_one(update_vo.get_key_field(), {"$set": update_vo.get_update_fields()})
        if result.matched_count == 0 and result.modified_count == 0:
            raise DataNotFound(table.name, update_vo.get_key_field())
        return result

    def list(self):
        table = self._get_table()
        result = table.find({})
        return result

    def get_by_id(self, id: UUID):
        table = self._get_table()
        return table.find_one({"id": id})

    def delete_by_id(self, id: UUID):
        table = self._get_table()
        result = table.delete_one({"id": id})
        if result.deleted_count == 0:
            raise DataNotFound(table.name, {"id": id})

    def get_by_criteria(self, search_criteria: dict):
        table = self._get_table()
        result = table.find_one(search_criteria)
        if result is None:
            raise DataNotFound(table.name, search_criteria)
        return result

    def delete_by_criteria(self, search_criteria: dict):
        table = self._get_table()
        result = table.delete_one(search_criteria)
        if result.deleted_count == 0:
            raise DataNotFound(table.name, search_criteria)

    def _get_table(self) -> Collection:
        return self.connection.get_connection()[self.get_table_name()]

