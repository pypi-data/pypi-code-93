''' Module to train a predictor. '''
import argparse
import logging
import soil
from soil.modules.retrain_predictor import retrain_predictor


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def train_predictor():
    ''' Main function to train a predictor. '''
    data = soil.data('iris')
    predictor_ref, = retrain_predictor(data)
    soil.alias('predictor', predictor_ref)


def main():
    ''' Argument parsing. '''
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    train_predictor(**vars(args))


if __name__ == '__main__':
    main()
