''' A module to create a generic datastructure to index stuff to Elastic Search '''

from soil import modulify
from soil.data_structures.es_data_structure import ESDataStructure


@modulify(output_types=lambda *input_types, **args: [ESDataStructure])
def to_es_data_structure(input_data):
    ''' A module to create a generic datastructure to index stuff to Elastic Search '''
    return [ESDataStructure(input_data.data, metadata=input_data.metadata)]
