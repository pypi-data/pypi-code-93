import pymongo
from pymongo.errors import BulkWriteError
import logging

from sre_snapshots.read_snapshots import mongodb_connect
from sre_snapshots.utils import safe_encode_document, format_dates, update_big_ints


def upload_result(result, host: str, port: int = 27017, db_name='sre_snapshots', collection_name='serpapi_results'):
    client = mongodb_connect(host, port)
    db = client[db_name]
    collection = db[collection_name]
    result_safe = safe_encode_document(result)
    result_safe_formatted = format_dates(result_safe)
    try:
        res = collection.insert_one(result_safe_formatted)
    except OverflowError as oe:
        logging.error(f'There was a problem with the inserting the snapshot into MongoDB. '
                      f'Please see the snapshot that caused the error below. '
                      f'The exact error message is: {oe}')
        print(result_safe_formatted)
        res = None
    return res


def upload_results(results, db_name='sre_snapshots', collection_name='serpapi_results'):
    """
    Insert SerpApi results into a MongoDB.
    :param results: A list of Google Search snapshots downloaded from SerpApi
    :type results: list of dict
    :param db_name: Name of the MongoDB database to insert results into.
    :type db_name: str
    :param collection_name: Name of the collection to house the data.
    :return: List of inserted object IDs
    :rtype: list of bson.objectid.ObjectId
    """
    client = mongodb_connect()
    db = client[db_name]
    collection = db[collection_name]

    results_safe = [safe_encode_document(doc) for doc in results]  # JSON encoding
    results_safe_formatted = [format_dates(doc) for doc in results_safe]  # format dates
    results_safe_formatted_smallint = [update_big_ints(doc) for doc in results_safe_formatted]  # remove > 8-byte ints

    try:
        res = collection.insert_many(results_safe_formatted_smallint)
    except BulkWriteError as bwe:
        logging.error(bwe.details)
        raise
    except OverflowError as oe:
        logging.error(f'There was a problem with the inserting the snapshot into MongoDB. '
                      f'Please see the snapshot that caused the error below. '
                      f'The exact error message is: {oe}')
        res = None
    return res


def main():
    pass


if __name__ == '__main_':
    main()
