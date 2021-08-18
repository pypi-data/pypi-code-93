''' A generic datastructure to index stuff to Elastic Search '''
import logging
import statistics
from soil.data_structures.streams.stream import Stream
from soil.connectors.elastic_search import create_db_object

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def _row_to_action(index, _metadata):
    def function(row):
        return {
            '_index': index,
            ** row
        }
    return function


class ESDataStructure(Stream):
    ''' A generic datastructure to index stuff to Elastic Search '''
    @staticmethod
    def unserialize(data, metadata, db_object=None):
        ''' Extract data from ES'''
        if data is not None:
            raise NotImplementedError('ESDataStructure without ES not implemented')
        if db_object is not None and db_object.type == 'ElasticSearch':
            if db_object.partial_query is None:
                db_object.update_query({})
            return ESDataStructure(None, metadata, db_object)
        raise NotImplementedError('ESDataStructure without ES not implemented')

    def db_unserializer(self, data):
        ''' Unserialize data. Method needed by Stream'''
        # pylint: disable=no-self-use
        return (d for d in data[0])

    def get_data(self, query=None, source=None, action=None):
        ''' Serialize the data for JSON the data '''
        if query is None:
            query = {
                "match_all": {}
            }
        if source is not None:
            question = {'query': query, '_source': source}
        else:
            question = {'query': query}

        response = list(self.db_object.query(question)[0])

        if action == 'count':
            return len(response)
        if action == 'source_avg':
            return statistics.mean(i[source] for i in response)

        return response

    def serialize(self):
        ''' Puts the data in Elastic Search '''
        rewrite = self.metadata.get('rewrite', False)
        index_name = self.metadata['index']
        es_db_object = create_db_object(index=index_name, force_rewrite=rewrite)
        data = self.data
        actions = map(_row_to_action(index_name, self.metadata), data)
        es_db_object.bulk(actions)
        return es_db_object
