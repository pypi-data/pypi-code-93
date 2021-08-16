import pymongo
import logging
from typing import Optional
from bson.objectid import ObjectId

from sre_snapshots.utils import valid_date_range


class SnapshotLibrary:

    def __init__(self,
                 host: str,
                 port: int = 27017,
                 database_name: str = 'sre_snapshots',
                 collection_name: str = 'serpapi_results'):
        """
        Connect to a MongoDB collection.
        :param host:
        :param port:
        :param database_name:
        :param collection_name:
        """
        self.host = host
        self.port = port
        self.database_name = database_name
        self.collection_name = collection_name

    @property
    def client(self) -> pymongo.MongoClient:
        return pymongo.MongoClient(host=self.host, port=self.port)

    @property
    def db(self):
        return self.client[self.database_name]

    @property
    def collection(self) -> pymongo.collection.Collection:
        return self.db[self.collection_name]

    @staticmethod
    def parse_object_id(object_id: str):
        return ObjectId(object_id)

    def find_documents(self,
                       filter_criteria: Optional[dict] = None,
                       object_id: Optional[str] = None,
                       datetime_from: Optional[str] = None,
                       datetime_to: Optional[str] = None,
                       limit: int = 0,
                       include_id: bool = False,
                       include_html: bool = False,) -> list:
        """
        Download documents matching a set of criteria from a MongoDB collection.
        :param filter_criteria: Dictionary of MongoDB-style filters to include in the query. ``None`` to retrieve all docs
            within the date range.
        :param object_id: The ObjectID of the record.
        :param datetime_from: Date to filter snapshots created after a particular date in %Y-%m-%d %H:%M:%S
          (YYYY-mm-dd HH:MM:SS) format.
        :param datetime_to: Date to filter snapshots created up to a particular date in %Y-%m-%d %H:%M:%S
          (YYYY-mm-dd HH:MM:SS) format.
        :param limit: Total number of documents to download. A limit of 0 (the default) is equivalent to setting no limit
        :param include_id: Whether to exclude the default '_id' field.
        :param include_html: Whether or not to download the 'search_metadata.raw_html_doc' element, which contains the
            full HTML document for the SERP.
        :return: Matching documents, if there are any.
        """

        # TODO parse Object ID filter

        # Validate both datetime inputs
        try:
            datetime_from, datetime_to = valid_date_range(datetime_from, datetime_to)
        except AssertionError as ae:
            logging.error(f'There is a problem with your datetime inputs: {ae}')
        except Exception as e:
            logging.error(f'An unexpected error occurred: {e}')

        filter_criteria = dict() if filter_criteria is None else filter_criteria

        if object_id:
            filter_criteria['_id'] = self.parse_object_id(object_id)

        # Quick count of number of documents that match
        doc_count = self.collection.count_documents({
            'search_metadata.created_at': {'$gt': datetime_from, '$lt': datetime_to},
            **filter_criteria
        })

        if doc_count > 0:
            logging.info(f'{doc_count} documents in total identified that match criteria')
            if include_id:
                cursor = self.collection.find({
                    'search_metadata.created_at': {'$gt': datetime_from, '$lt': datetime_to},
                    **filter_criteria
                }, limit=limit)
            else:
                cursor = self.collection.find({
                    'search_metadata.created_at': {'$gt': datetime_from, '$lt': datetime_to},
                    **filter_criteria
                }, limit=limit, projection={'_id': include_id, 'search_metadata.raw_html_doc': include_html})
            return [doc for doc in cursor]
        else:
            logging.warning('No documents found that match your filter criteria')
            return []

    @property
    def database_exists(self) -> bool:
        """
        Check whether a database exists in MongoDB.
        :return: True or False
        """
        db_list = self.client.list_database_names()
        if self.database_name in db_list:
            return True
        else:
            return False


def main():
    pass


if __name__ == '__main_':
    main()
