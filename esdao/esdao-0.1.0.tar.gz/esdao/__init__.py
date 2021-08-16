from elasticsearch import Elasticsearch, helpers
from abc import abstractmethod, ABCMeta
from typing import Dict, List
from esdao.dsl import Match, DslBoolQuery
from collections import deque


# ---------------------------------------------------------
# DOCUMENT QUERY FORMAT ERROR
# ---------------------------------------------------------
class DocumentQueryFormatError(Exception):
    pass


# ---------------------------------------------------------
# DOCUMENT NOT FOUND ERROR
# ---------------------------------------------------------
class DocumentNotFoundError(Exception):
    pass


# ---------------------------------------------------------
# DOCUMENT DSL QUERY ADAPTER
# ---------------------------------------------------------
class DocumentBoolMatchDslQueryAdapter(object):
    def __init__(self, query: dict):
        self.query: dict = query
        self.dsl_query = DslBoolQuery()

    def build_dsl_query(self):
        try:
            for field in self.query.keys():
                # TODO find a more elegant way of parsing the queries
                if self.query[field].keys()[0] == 'eq':
                    self.dsl_query.must(Match(field, self.query[field]['eq']))
                elif self.query[field].keys()[0] == 'neq':
                    self.dsl_query.must_not(Match(field, self.query[field]['eq']))
        except Exception:
            raise DocumentQueryFormatError('Invalid query format')

    def query_as_dict(self) -> dict:
        return self.dsl_query.dict()


# ---------------------------------------------------------
# ELASTIC ENTITY REPOSITORY BASE
# ---------------------------------------------------------
class ElasticEntityRepositoryBase(object):
    __metaclass__ = ABCMeta

    # -----------------------------------------------------
    # CONSTRUCTOR METHOD
    # -----------------------------------------------------
    def __init__(
            self,
            index: str,
            elasticsearch_client: Elasticsearch
    ):
        self.index = index
        self.elasticsearch_client: Elasticsearch = \
            elasticsearch_client

    # -----------------------------------------------------
    # QUERY
    # -----------------------------------------------------
    def search(self, query: dict) -> List[Dict]:
        """
        TODO
        :param query: A query with format: {'field_name_1': {'eq': 'value_1'},
        {'field_name_2': {'neq': 'value_2'}}
        :return:
        """
        q = DocumentBoolMatchDslQueryAdapter(query=query).query_as_dict()
        result = self.elasticsearch_client.search(
            index=self.index,
            body=q,
            scroll='1m'
        )
        matches: List[Dict] = []
        if 'hits' in result and 'hits' in result['hits']:
            for match in result['hits']['hits']:
                matches.append(match['_source'])
        return matches

    # -----------------------------------------------------
    # QUERY
    # -----------------------------------------------------
    def get(self, document_id: str) -> Dict or None:
        result = self.elasticsearch_client.get(
            index=self.index,
            id=document_id
        )
        if result is not None and '_source' in result:
            return result['_source']
        return None

    # -----------------------------------------------------
    # CREATE
    # -----------------------------------------------------
    def create(self, document: dict, document_id: str):
        return self.elasticsearch_client.index(
            index=self.index,
            id=document_id,
            body=document
        )

    # -----------------------------------------------------
    # CREATE MANY
    # -----------------------------------------------------
    def create_many(self, documents: List[Dict], id_key):
        """
        From Elasticsearch documentation:

        The bulk() api accepts index, create, delete,
        and update actions. Use the _op_type field to
        specify an action (_op_type defaults to index

         TODO implement other bulk actions
        :param documents:
        :param id_key:
        :return:
        """
        bulk_operations = []
        for document in documents:
            bulk_operations.append(
                {
                    "_op_type": "index",
                    "_index": self.index,
                    "_id": document[id_key],
                    "_source": document
                }
            )
        return deque(helpers.parallel_bulk(
            self.elasticsearch_client,
            bulk_operations,
            thread_count=20
        ), maxlen=0)

    # -----------------------------------------------------
    # UPDATE
    # -----------------------------------------------------
    def update(self, document_id: str, fields: dict):
        doc = self.get(document_id=document_id)
        if doc:
            for key in fields.keys():
                doc[key] = fields[key]
            return self.elasticsearch_client.index(
                index=self.index,
                id=document_id,
                body=doc
            )
        raise DocumentNotFoundError(
            f'Unable to find document with id: {document_id}'
        )