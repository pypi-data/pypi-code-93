#!/usr/bin/env python3
import time
from pymongo import MongoClient, errors, response, cursor
from socket import error as GenericSocketError
from typing import Union

"""mongoblack: MongoDB handlers to streamline application interfaces"""

__author__ = "Brandon Blackburn"
__maintainer__ = "Brandon Blackburn"
__email__ = "contact@bhax.net"
__website__ = "https://keybase.io/blackburnhax"
__copyright__ = "Copyright 2021, Brandon Blackburn"
__license__ = "Apache 2.0"

#  Copyright (c) 2021. Brandon Blackburn - https://keybase.io/blackburnhax, Apache License, Version 2.0.
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#  http://www.apache.org/licenses/LICENSE-2.0
#  Unless required by applicable law or agreed to in writing,
#  software distributed under the License is distributed on an
#  "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
#  either express or implied. See the License for the specific
#  language governing permissions and limitations under the License.
#  TL;DR:
#  For a human-readable & fast explanation of the Apache 2.0 license visit:  http://www.tldrlegal.com/l/apache2


class Connection:
    def __init__(self, instance: str, user: str, password: str, mdb_string: str, **kwargs: object):
        """
        :param instance: MongoDB server instance name
        :param user: MongoDB instance user name
        :param password: MongoDB instance user password
        :param mdb_string: MongoDB connection string
        :keyword compression: Zlib compression level (default: 1)
        :keyword tls: SSL/TLS state (default: True)
        :keyword retries: Number of attempted retries for operations
        :keyword timeout: Cool-down period in seconds between successive retries (default: 0.5)
        """
        if not isinstance(instance, str):
            raise ValueError("instance parameter must be a string")

        if not isinstance(user, str):
            raise ValueError("user parameter must be a string")

        if not isinstance(password, str):
            raise ValueError("password parameter must be a string")

        if isinstance(mdb_string, str):
            self.mdb_string = str(mdb_string).strip()
        else:
            raise ValueError("mdb_string parameter must be a string")

        compression = kwargs.get("compression", 1)
        if isinstance(compression, int):
            if compression < 0:
                raise ValueError("compression keyword is less than zero")
        else:
            raise ValueError("Compression keyword must be an integer or left undefined")

        tls = kwargs.get("tls", True)
        if not isinstance(tls, bool):
            raise ValueError("tls keyword must be a string")

        self.retries = kwargs.get("retries", -1)
        if isinstance(self.retries, int):
            if not self.retries >= -1:
                raise ValueError("retries keyword must be greater than or equal to -1 or left undefined")
        else:
            raise ValueError("retries keyword must be greater than or equal to -1 or left undefined")

        self.timeout = kwargs.get("timeout", 0.5)
        if isinstance(self.timeout, (int, float)):
            if self.timeout <= 0:
                raise ValueError("timeout keyword must be a number greater than zero or left undefined")
        else:
            raise ValueError("timeout keyword must be a number greater than zero or left undefined")

        self.server = MongoClient(
            self.mdb_string,
            authSource=instance,
            appname=instance,
            document_class=dict,
            username=user,
            password=password,
            retryWrites=True,
            zlibCompressionLevel=compression,
            ssl=tls,
            tz_aware=True,
        )
        self.db = self.server[instance]

    def _retry(func):
        def wrapped(*args, **kwargs):
            attempts = 0
            while args[0].retries == -1 or attempts < args[0].retries:
                attempts += 1
                try:
                    return func(*args, **kwargs)
                except errors.BulkWriteError:
                    raise InterruptedError("Bulk write operation failed.")
                except errors.WriteError:
                    raise InterruptedError("Write operation failed.")
                except errors.InvalidURI:
                    raise ConnectionAbortedError("Provided mdb_string is invalid.")
                except errors.ConfigurationError:
                    raise PermissionError("Provided credentials to database are invalid.")
                except errors.DocumentTooLarge:
                    raise ValueError("Dictionary provided to database was too large.")
                except errors.DuplicateKeyError:
                    raise LookupError("Attempted to write to an existing database key.")
                except errors.ServerSelectionTimeoutError:
                    print(f"Network timeouts when attempting initial database connection")
                except errors.NetworkTimeout:
                    print(f"Network timeouts when attempting to reach database")
                except errors.AutoReconnect:
                    print("Resuming database connection...")
                except errors.CursorNotFound:
                    print("Restarting database connection...")
                except GenericSocketError:
                    print("Unspecified network socket error in database connection. Retrying connection...")
                time.sleep(args[0].timeout)
            raise ConnectionError(f"Unable to connect to database after {attempts} attempts.")

        return wrapped

    @_retry
    def write(self, collection: str, dictionary: dict, key: Union[str, int]) -> response:
        """
        Writes the dictionary inside the document identified by the key, within the specified collection.
        Creates the document if one does not already exist, updates the document if it does exist.
        :param collection: Collection to use
        :param dictionary: Document body
        :param key: Key to use when writing
        :return:
        """
        return self.db[collection].update_one({"_id": key}, {"$set": dictionary}, upsert=True)

    @_retry
    def write_new(self, collection: str, dictionary: dict) -> response:
        """
        Writes the given dictionary as a new document within the provided collection using a generative key.
        :param collection: Collection to use
        :param dictionary: Document body
        :return:
        """
        return self.db[collection].insert_one(dictionary)

    @_retry
    def overwrite(self, collection: str, dictionary: dict, key: Union[str, int]) -> response:
        """
        Overwrites the given document within the provided collection.
        :param collection: Collection to use
        :param dictionary: Document body
        :param key: Key to use when writing
        :return:
        """
        return self.db[collection].replace_one({"_id": key}, dictionary)

    @_retry
    def get(self, collection: str, key: Union[str, int]) -> response:
        """
        Retrieve a document in the given collection specified by the key
        :param collection: Collection to use
        :param dictionary: Document body
        :param key: Key to retrieve
        :return: dictionary of the document
        """
        return self.db[collection].find_one({"_id": key})

    @_retry
    def delete(self, collection: str, key: Union[str, int]) -> response:
        """
        Delete the document in the given collection specified by the key
        :param collection: Collection to use
        :param dictionary: Document body
        :param key: Key to delete
        :return:
        """
        return self.db[collection].delete_one({"_id": key})

    @_retry
    def delete_branch(self, collection: str, key: Union[str, int], branch: Union[str, int]) -> response:
        """
        Delete the document branch in the given key
        :param collection: Collection to use
        :param dictionary: Document body
        :param key: Key to update
        :param branch: Branch to delete
        :return:
        """
        return self.db[collection].update_one({"_id": key}, {"$unset": {branch: 1}})

    @_retry
    def get_all(self, collection: str, query: str = None) -> cursor:
        """
        Retrieve all matching documents in the given collection.
        If query is not specified, pulls all documents in the collection
        :param collection: Collection to use
        :param query: Dictionary containing PyMongo compliant query.
        :return: iterable of each dictionary (document) found
        """
        if query is None:
            return self.db[collection].find(batch_size=0)
        else:
            return self.db[collection].find(query, batch_size=0)

    @_retry
    def count(self, collection: str, query: str = None) -> int:
        """
        Retrieve a count of all matching documents in the given collection.
        If query is not specified, counts all documents in the collection
        :param collection: Collection to use
        :param query: Dictionary containing PyMongo compliant query.
        :return: integer count of documents in collection
        """
        if query is None:
            return self.db[collection].count_documents({})
        else:
            return self.db[collection].count_documents(query)

    @_retry
    def copy(self, source: str, destination: str) -> response:
        """
        Copies the entire contents of a collection to a new destination collection
        :param source: Collection to copy
        :param destination: Name of new collection to create
        :return: aggregation result
        """
        operation = [{"$match": {}}, {"$out": destination}]
        return self.db[source].aggregate(operation)

    @_retry
    def new_reference_collection(self, source: str, destination: str) -> response:
        """
        Copies just the reference keys of an entire collection to a new destination collection.
        This operation is much faster than a full copy()
        :param source: Collection to copy
        :param destination: Name of new collection to create
        :return: aggregation result
        """
        operation = [
            {"$match": {}},
            {"$project": {"_id": 1}},
            {"$out": destination},
        ]
        return self.db[source].aggregate(operation)

    copy_reference = new_reference_collection
