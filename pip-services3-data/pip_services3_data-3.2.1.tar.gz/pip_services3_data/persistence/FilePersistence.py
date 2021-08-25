# -*- coding: utf-8 -*-
"""
    pip_services3_data.persistence.FilePersistence
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    File persistence implementation.
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Optional

from pip_services3_commons.config import IConfigurable, ConfigParams

from .JsonFilePersister import JsonFilePersister
from .MemoryPersistence import MemoryPersistence


class FilePersistence(MemoryPersistence, IConfigurable):
    """
    Abstract persistence component that stores data in flat files
    and caches them in memory.

    This is the most basic persistence component that is only
    able to store data items of any type. Specific CRUD operations
    over the data items must be implemented in child classes by
    accessing self._items property and calling :func:save method.

    ### Configuration parameters ###
        - path:                path to the file where data is stored

    ### References ###
        - `*:logger:*:*:1.0`   (optional) ILogger components to pass log messages

    Example:

    .. code-block:: python

       class MyJsonFilePersistence(FilePersistence):
           def __init__(self, path):
               super(MyJsonFilePersistence, self).__init__(JsonPersister(path))

           def get_by_name(self, correlationId, name):
               item = self.find(name)
               ...
               return item
    """
    _persister: JsonFilePersister = None

    def __init__(self, persister: Optional[JsonFilePersister] = None):
        """
        Creates a new instance of the persistence.

        :param persister: (optional) a persister component that loads and saves data from/to flat file.
        """
        super(FilePersistence, self).__init__(persister if not (persister is None) else JsonFilePersister(),
                                              persister if not (persister is None) else JsonFilePersister())

        self._persister = persister
        # self._saver = self._persister
        # self._loader = self._persister

    def configure(self, config: ConfigParams):
        """
        Configures component by passing configuration parameters.

        :param config: configuration parameters to be set.
        """
        self._persister.configure(config)
