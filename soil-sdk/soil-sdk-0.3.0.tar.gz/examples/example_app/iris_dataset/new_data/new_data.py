''' This program runs when new data arrives. '''
import logging
import argparse
import json
import soil
from soil.modules.to_es_data_structure import to_es_data_structure
from ..lib.utils import get_columns_dictnames, read_data

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def _new_data(input_file=None, schema_file=None):

    # Read schema
    schema = json.load(schema_file)
    columns = get_columns_dictnames(schema['columns'])

    # Read data
    data = read_data(input_file)
    data_ref = soil.data(data, metadata={'columns': columns, 'index': 'simple-data'})
    res, = to_es_data_structure(data_ref)
    soil.alias('iris', res)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', type=argparse.FileType('r'), help='The input file')
    parser.add_argument('--schema-file', type=argparse.FileType('r'),
                        help='The file with the schema of the data', required=True)
    args = parser.parse_args()
    _new_data(**vars(args))
