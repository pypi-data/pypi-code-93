"""
An indentity lemmatizer that mimics the behavior of a normal lemmatizer but directly uses word as lemma.
"""

import os
import argparse
import random

from classla.models.lemma.data import DataLoader
from classla.models.lemma import scorer
from classla.models.common import utils
from classla.models.common.doc import *
from classla.utils.conll import CoNLL
from classla.models import _training_logging

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir', type=str, default='data/lemma', help='Directory for all lemma data.')
    parser.add_argument('--train_file', type=str, default=None, help='Input file for data loader.')
    parser.add_argument('--eval_file', type=str, default=None, help='Input file for data loader.')
    parser.add_argument('--output_file', type=str, default=None, help='Output CoNLL-U file.')
    parser.add_argument('--gold_file', type=str, default=None, help='Output CoNLL-U file.')

    parser.add_argument('--mode', default='train', choices=['train', 'predict'])
    parser.add_argument('--lang', type=str, help='Language')

    parser.add_argument('--batch_size', type=int, default=50)
    parser.add_argument('--seed', type=int, default=1234)
    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    random.seed(args.seed)

    args = vars(args)

    print("[Launching identity lemmatizer...]")

    if args['mode'] == 'train':
        print("[No training is required; will only generate evaluation output...]")

    doc, metasentences = CoNLL.conll2dict(input_file=args['eval_file'])
    document = Document(doc, metasentences=metasentences)
    batch = DataLoader(document, args['batch_size'], args, evaluation=True, conll_only=True)
    system_pred_file = args['output_file']
    gold_file = args['gold_file']

    # use identity mapping for prediction
    preds = batch.doc.get([TEXT])

    # write to file and score
    batch.doc.set([LEMMA], preds)
    CoNLL.dict2conll(batch.doc.to_dict(), system_pred_file)
    if gold_file is not None:
        _, _, score = scorer.score(system_pred_file, gold_file)

        print("Lemma score:")
        print("{} {:.2f}".format(args['lang'], score*100))

if __name__ == '__main__':
    main()
