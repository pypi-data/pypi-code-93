# -*- coding: utf-8 -*-
"""
    pip_services3_data.persistence.__init__
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Pip-services-data.persistence initialisation.

    Contains various persistence implementations (InMemory
    and File –persistences). These are"abstract" persistences,
    which only connect to data sources and do not implement the operations
    and methods for working the data. The classes that extend these
    persistences must implement this logic on their own.

    Identifiable Persistences work with Identifiable objects,
    which have primary keys. A few standard operations are defined
    by default for these objects: reading arrays and data pages;
    searching for an object by its id; and creating, updating,
    and deleting records of objects.

    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

__all__ = ['MemoryPersistence', 'IdentifiableMemoryPersistence',
           'FilePersistence', 'IdentifiableFilePersistence', 'JsonFilePersister']

from .MemoryPersistence import MemoryPersistence
from .IdentifiableMemoryPersistence import IdentifiableMemoryPersistence
from .FilePersistence import FilePersistence
from .IdentifiableFilePersistence import IdentifiableFilePersistence
from .JsonFilePersister import JsonFilePersister