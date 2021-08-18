'''
    DataStructure to serialize PredictionsCombinations
    It stores the data to ElasticSearch.
'''

from datetime import datetime
from soil.data_structures.es_data_structure import ESDataStructure


def _row_to_action(index, _metadata):
    def action_fn(index_row):
        _i, row = index_row
        return {
            '_index': index,
            'generated_at': datetime.now(),
            ** row.to_dict()
        }
    return action_fn


class Predictions(ESDataStructure):
    '''
    DataStructure to serialize PredictionsCombinations
    It stores the data to ElasticSearch.
    '''
    def _row_to_action(self, *args):
        # pylint: disable=no-self-use
        return _row_to_action(*args)
