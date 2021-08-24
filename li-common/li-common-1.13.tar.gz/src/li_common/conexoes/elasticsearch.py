# from li_common.helpers import tente_outra_vez

from pyelasticsearch import ElasticSearch
from requests import ConnectionError

# Existe apenas para repasse de exceptions via heranca
from pyelasticsearch import exceptions as ElasticsearchExceptions

class ElasticsearchConnect(object):

    def __init__(self,elasticsearch_url):
        self.server = self.set_server(elasticsearch_url)

    @classmethod
    def set_server(self, url):

        if hasattr(self,'servers') is False:
            self.servers = {}

        if url not in self.servers:
            self.servers[url] = ElasticSearch(url, max_retries=3)

        return self.servers[url]

    def get(self, index, doc_type, id, **kwargs):
        return self.server.get(index, doc_type, id, **kwargs)

    def search(self, query, **kwargs):
        return self.server.search(query, **kwargs)

    # @tente_outra_vez(ConnectionError, tentativas=4, tempo_espera=3, multiplicador_espera=2)
    def index(self, index, content_type, content, **kwargs):
        return self.server.index(index, content_type, content, **kwargs)

    def bulk_index(self, index, doc_type, docs, **kwargs):
        return self.server.bulk_index(index, doc_type, docs, **kwargs)

    def delete_by_query(self, index, doc_type, **kwargs):
        return self.server.delete_by_query(index, doc_type, **kwargs)

    def delete(self, index, doc_type, id, **kwargs):
        return self.server.delete(index, doc_type, id, **kwargs)