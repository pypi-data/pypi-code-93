''' This program runs when new data arrives. '''
import logging
import argparse
import soil
from soil.modules.to_es_data_structure import to_es_data_structure

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def _reset_dbs():
    logging.info('Cleaning index: simple-data')
    data = []
    data_ref = soil.data(data, metadata={'index': 'simple-data', 'rewrite': True})
    res, = to_es_data_structure(data_ref)
    soil.alias('iris', res)
    logging.info('Cleaning index: simple-preds')
    data_ref = soil.data(data, metadata={'index': 'simple-preds', 'rewrite': True})
    res, = to_es_data_structure(data_ref)
    soil.alias('preds', res)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    _reset_dbs(**vars(args))
