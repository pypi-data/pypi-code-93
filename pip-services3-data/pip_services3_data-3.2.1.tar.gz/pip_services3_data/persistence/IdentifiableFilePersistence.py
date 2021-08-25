# -*- coding: utf-8 -*-
"""
    pip_services3_data.persistence.IdentifiableFilePersistence
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Identifiable file persistence implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Optional

from pip_services3_commons.config import ConfigParams
from pip_services3_commons.data import IIdentifiable

from .IdentifiableMemoryPersistence import IdentifiableMemoryPersistence
from .JsonFilePersister import JsonFilePersister


class IdentifiableFilePersistence(IdentifiableMemoryPersistence, IIdentifiable):
    """
    Abstract persistence component that stores data in flat files
    and implements a number of CRUD operations over data items with
    unique ids. The data items must implement :class:`IIdentifiable <pip_services3_commons.data.IIdentifiable.IIdentifiable>` interface.

    In basic scenarios child classes shall only override
    :func:`get_page_by_filter`, :func:`get_list_by_filter` or :func:`delete_by_filter`
    operations with specific filter function. All other operations can be
    used out of the box. In complex scenarios child classes can implement
    additional operations by accessing cached items via self._items
    property and calling :func:`save` method on updates.

    ### Configuration parameters ###
        - path:                    path to the file where data is stored
        - options:
            - max_page_size:       Maximum number of items returned in a single page (default: 100)

    ### References ###
        - `*:logger:*:*:1.0`       (optional) ILogger components to pass log messages

    Example:

    .. code-block:: python
    
        class MyFilePersistence(IdentifiableFilePersistence):
            def __init__(self, path):
                super(MyFilePersistence, self).__init__(JsonPersister(path))

            def get_page_by_filter(self, correlationId, filter, paging):
                super().get_page_by_filter(correlationId, filter, paging, None)

            persistence = MyFilePersistence("./data/data.json")

            item = persistence.create("123", MyData("1", "ABC"))

            mydata = persistence.get_page_by_filter("123", FilterParams.from_tuples("name", "ABC"), None, None)
            print str(mydata.get_data())

            persistence.delete_by_id("123", "1")
            
    """
    _persister: JsonFilePersister = None

    def __init__(self, persister: Optional[JsonFilePersister] = None):
        """
        Creates a new instance of the persistence.

        :param persister: (optional) a persister component that loads and saves data from/to flat file.
        """
        super(IdentifiableFilePersistence, self).__init__(persister if not (persister is None) else JsonFilePersister(),
                                                          persister if not (persister is None) else JsonFilePersister())

        self._persister = persister
        # self._saver = self._persister
        # self._loader = self._persister

    def configure(self, config: ConfigParams):
        """
        Configures component by passing configuration parameters.

        :param config: configuration parameters to be set.
        """
        super().configure(config)
        self._persister.configure(config)
