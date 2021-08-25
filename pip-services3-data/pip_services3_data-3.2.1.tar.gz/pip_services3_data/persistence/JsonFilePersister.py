# -*- coding: utf-8 -*-
"""
    pip_services3_data.persistence.JsonFilePersister
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    JSON file persister implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

import json
import os
from typing import Optional, List, TypeVar

from pip_services3_commons.config import IConfigurable, ConfigParams
from pip_services3_commons.errors import ConfigException, FileException
from pip_services3_commons.reflect import ObjectReader

from ..ILoader import ILoader
from ..ISaver import ISaver

T = TypeVar('T')  # Declare type variable


class JsonFilePersister(ILoader, ISaver, IConfigurable):
    """
    Persistence component that loads and saves data from/to flat file.

    It is used by :class:`FilePersistence <pip_services3_data.persistence.FilePersistence.FilePersistence>`, but can be useful on its own.

    ### Configuration parameters ###
        - path:          path to the file where data is stored

    Example:

    .. code-block:: python
    
        persister = JsonFilePersister("./data/data.json")

        persister.save("123", ["A", "B", "C"])
        ...

        persister.load("123", items)
        print items
    """

    def __init__(self, path: str = None):
        """
        Creates a new instance of the persistence.

        :param path: (optional) a path to the file where data is stored.
        """
        self.__path = path

    @property
    def path(self) -> str:
        """
        Gets the file path where data is stored.

        :returns: the file path where data is stored.
        """
        return self.__path

    @path.setter
    def path(self, value: str):
        """
        Sets the file path where data is stored.

        :param value: the file path where data is stored.
        """
        self.__path = value

    def configure(self, config: ConfigParams):
        """
        Configures component by passing configuration parameters.

        :param config: configuration parameters to be set.
        """
        try:
            if config is not None or config.get("path"):
                self.__path = config.get_as_string("path")

        except AttributeError:
            raise ConfigException(None, "NO_PATH", "Data file path is not set")

    def load(self, correlation_id: Optional[str]) -> List[T]:
        """
        Loads data items from external JSON file.

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :return: loaded items
        """
        # If doesn't exist then consider empty data
        if not os.path.isfile(self.__path):
            return []

        try:
            with open(self.__path, 'r') as file:
                return json.load(file)
        except Exception as ex:
            raise FileException(correlation_id, "READ_FAILED", "Failed to read data file: " + str(ex)) \
                .with_cause(ex)

    def save(self, correlation_id: Optional[str], items: List[T]):
        """
        Saves given data items to external JSON file.

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :param items: list if data items to save
        """
        try:
            list_props = []
            for item in items:
                list_props.append(ObjectReader.get_properties(item))

            with open(self.__path, 'w') as file:
                json.dump(list_props, file)
        except Exception as ex:
            raise FileException(correlation_id, "WRITE_FAILED", "Failed to write data file: " + str(ex)) \
                .with_cause(ex)
