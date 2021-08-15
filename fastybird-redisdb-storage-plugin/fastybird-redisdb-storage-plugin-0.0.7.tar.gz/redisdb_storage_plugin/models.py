#!/usr/bin/python3

#     Copyright 2021. FastyBird s.r.o.
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.

"""
Storage models
"""

# Library dependencies
from datetime import datetime
import json
import uuid
from typing import Dict, Type
from abc import ABC
from redis import Redis

# Library libs
from redisdb_storage_plugin.exceptions import InvalidStateException
from redisdb_storage_plugin.state import StorageItem


class StorageRepository(ABC):
    """
    Storage repository

    @package        FastyBird:RedisDbStoragePlugin!
    @module         models

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """
    __redis_client: Redis
    __entity: Type[StorageItem]

    # -----------------------------------------------------------------------------

    def __init__(self, host: str, port: int, entity: Type[StorageItem] = StorageItem) -> None:
        self.__redis_client = Redis(host, port)

        self.__entity = entity

    # -----------------------------------------------------------------------------

    def find_one(self, item_id: uuid.UUID) -> StorageItem or None:
        """Fin one storage item in database by identifier"""
        storage_key: str = item_id.__str__()

        stored_data = self.__redis_client.get(storage_key)

        if stored_data is None:
            return None

        if isinstance(stored_data, bytes):
            stored_data = stored_data.decode("utf-8")

        try:
            stored_data_dict: dict = json.loads(stored_data)

            return self.__entity(
                item_id=item_id,
                raw=stored_data_dict,
            )

        except json.JSONDecodeError as ex:
            # Stored value is invalid, key should be removed
            self.__redis_client.delete(storage_key)

            raise InvalidStateException(
                "Storage data for key: {} could not be loaded from storage. Json error".format(storage_key)
            ) from ex

    # -----------------------------------------------------------------------------

    def close(self) -> None:
        """Close opened connection to Redis database"""
        self.__redis_client.close()

    def __del__(self):
        self.close()


class StorageManager(ABC):
    """
    Storage manager

    @package        FastyBird:RedisDbStoragePlugin!
    @module         models

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """
    __redis_client: Redis
    __storage_repository: StorageRepository
    __entity: Type[StorageItem]

    # -----------------------------------------------------------------------------

    def __init__(
            self,
            host: str,
            port: int,
            storage_repository: StorageRepository,
            entity: Type[StorageItem] = StorageItem
    ) -> None:
        self.__redis_client = Redis(host, port)

        self.__storage_repository = storage_repository
        self.__entity = entity

    # -----------------------------------------------------------------------------

    def create(self, item_id: uuid.UUID, values: Dict) -> StorageItem:
        """Create state item in storage"""
        data_to_write: Dict = dict()

        values["id"] = item_id.__str__()

        for key, value in self.__entity.create_fields().items():
            if isinstance(key, int) is True:
                field = value

                if field not in values.keys():
                    raise Exception("Value for key '{}' is required".format(field))

                field_value = values[field]

            else:
                field = key
                default = value

                if field in values.keys():
                    field_value = values[field]

                else:
                    if field == "created_at":
                        field_value = datetime.utcnow().strftime(r"%Y-%m-%d\T%H:%M:%S+00:00")

                    else:
                        field_value = default

            data_to_write[field] = field_value

        self.__redis_client.set(item_id.__str__(), json.dumps(data_to_write))

        try:
            stored_state: StorageItem or None = self.__storage_repository.find_one(item_id)

            if stored_state is None:
                raise InvalidStateException("Created item could not be fetched from database")

        except InvalidStateException as ex:
            self.__redis_client.delete(item_id.__str__())

            raise InvalidStateException("Created state record could not be fetched from database") from ex

        return stored_state

    # -----------------------------------------------------------------------------

    def update(self, state: StorageItem, values: Dict) -> StorageItem:
        """Update state item in storage"""
        raw_data = state.raw

        is_updated: bool = False

        for field in self.__entity.update_fields():
            if field in values.keys():
                field_value = values[field]

                if field not in raw_data or raw_data[field] != field_value:
                    raw_data[field] = field_value

                    is_updated = True

            elif field == "updated_at":
                raw_data[field] = datetime.utcnow().strftime(r"%Y-%m-%d\T%H:%M:%S+00:00")

        if is_updated:
            self.__redis_client.set(state.item_id.__str__(), json.dumps(raw_data))

        try:
            stored_state: StorageItem or None = self.__storage_repository.find_one(state.item_id)

            if stored_state is None:
                raise InvalidStateException("Updated item could not be fetched from database")

        except InvalidStateException as ex:
            self.__redis_client.delete(state.item_id.__str__())

            raise InvalidStateException("Updated state record could not be fetched from database") from ex

        return stored_state

    # -----------------------------------------------------------------------------

    def delete(self, state: StorageItem) -> bool:
        """Delete state item from storage"""
        if self.__redis_client.get(state.item_id.__str__()) is not None:
            self.__redis_client.delete(state.item_id.__str__())

            return True

        return False

    # -----------------------------------------------------------------------------

    def close(self) -> None:
        """Close opened connection to Redis database"""
        self.__redis_client.close()

    def __del__(self):
        self.close()
