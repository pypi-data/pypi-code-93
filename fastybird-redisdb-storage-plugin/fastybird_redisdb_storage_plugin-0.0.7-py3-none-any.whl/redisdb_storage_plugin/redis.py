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
Redis DB module
"""

# Library dependencies
from typing import Type

# Library libs
from redisdb_storage_plugin.models import StorageRepository, StorageManager
from redisdb_storage_plugin.state import StorageItem


class StorageSettings:
    """
    Redis storage configuration

    @package        FastyBird:RedisDbStoragePlugin!
    @module         redis

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """
    __host: str = "127.0.0.1"
    __port: int = 6379
    __username: str or None = None
    __password: str or None = None

    # -----------------------------------------------------------------------------

    def __init__(self, config: dict) -> None:
        self.__host = config.get("host", "127.0.0.1")
        self.__port = int(config.get("port", 6379))
        self.__username = config.get("user", None)
        self.__password = config.get("passwd", None)

    # -----------------------------------------------------------------------------

    @property
    def host(self) -> str:
        """Connection host"""
        return self.__host

    # -----------------------------------------------------------------------------

    @property
    def port(self) -> int:
        """Connection port"""
        return self.__port

    # -----------------------------------------------------------------------------

    @property
    def username(self) -> str or None:
        """Connection username"""
        return self.__username

    # -----------------------------------------------------------------------------

    @property
    def password(self) -> str or None:
        """Connection password"""
        return self.__password


def define_storage(config: dict, entity: Type[StorageItem] = StorageItem):
    """Initialize repository and manager"""
    settings: StorageSettings = StorageSettings(config)

    storage_repository = StorageRepository(settings.host, settings.port, entity)
    storage_manager = StorageManager(settings.host, settings.port, storage_repository, entity)

    return storage_repository, storage_manager
