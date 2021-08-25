"""
Entry point for training and evaluating a lemmatizer.

This lemmatizer combines a neural sequence-to-sequence architecture with an `edit` classifier 
and two dictionaries to produce robust lemmas from word forms.
For details please refer to paper: https://nlp.stanford.edu/pubs/qi2018universal.pdf.
"""

import sys
import os
import shutil
import time
from datetime import datetime
import argparse
import numpy as np
import random
import torch
from torch import nn, optim

from classla.models.lemma.data import DataLoader
from classla.models.lemma.vocab import Vocab
from classla.models.lemma.trainer import Trainer
from classla.models.lemma import scorer, edit
from classla.models.common import utils
import classla.models.common.seq2seq_constant as constant
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

    parser.add_argument('--no_dict', dest='ensemble_dict', action='store_false', help='Do not ensemble dictionary with seq2seq. By default use ensemble.')
    parser.add_argument('--dict_only', action='store_true', help='Only train a dictionary-based lemmatizer.')
    parser.add_argument('--external_dict', type=str, default=None, help='External dictionary in form (token, lemma, XPOS)')

    parser.add_argument('--hidden_dim', type=int, default=200)
    parser.add_argument('--emb_dim', type=int, default=50)
    parser.add_argument('--num_layers', type=int, default=1)
    parser.add_argument('--emb_dropout', type=float, default=0.5)
    parser.add_argument('--dropout', type=float, default=0.5)
    parser.add_argument('--max_dec_len', type=int, default=50)
    parser.add_argument('--beam_size', type=int, default=1)

    parser.add_argument('--attn_type', default='soft', choices=['soft', 'mlp', 'linear', 'deep'], help='Attention type')
    parser.add_argument('--pos', action='store_true', help='Use XPOS in lemmatization.')
    parser.add_argument('--pos_dim', type=int, default=50)
    parser.add_argument('--pos_dropout', type=float, default=0.5)
    parser.add_argument('--no_edit', dest='edit', action='store_false', help='Do not use edit classifier in lemmatization. By default use an edit classifier.')
    parser.add_argument('--num_edit', type=int, default=len(edit.EDIT_TO_ID))
    parser.add_argument('--alpha', type=float, default=1.0)
    parser.add_argument('--no_pos', dest='pos', action='store_false', help='Do not use UPOS in lemmatization. By default UPOS is used.')

    parser.add_argument('--sample_train', type=float, default=1.0, help='Subsample training data.')
    parser.add_argument('--optim', type=str, default='adam', help='sgd, adagrad, adam or adamax.')
    parser.add_argument('--lr', type=float, default=1e-3, help='Learning rate')
    parser.add_argument('--lr_decay', type=float, default=0.9)
    parser.add_argument('--decay_epoch', type=int, default=30, help="Decay the lr starting from this epoch.")
    parser.add_argument('--num_epoch', type=int, default=60)
    parser.add_argument('--batch_size', type=int, default=50)
    parser.add_argument('--max_grad_norm', type=float, default=5.0, help='Gradient clipping.')
    parser.add_argument('--log_step', type=int, default=20, help='Print log every k steps.')
    parser.add_argument('--model_dir', type=str, default='saved_models/lemma', help='Root dir for saving models.')
    parser.add_argument('--model_file', type=str, default='saved_models/lemma', help='File for saving models.')

    parser.add_argument('--seed', type=int, default=1234)
    parser.add_argument('--cuda', type=bool, default=torch.cuda.is_available())
    parser.add_argument('--cpu', action='store_true', help='Ignore CUDA.')
    args = parser.parse_args()
    return args

def main():
    sys.setrecursionlimit(50000)

    args = parse_args()

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    random.seed(args.seed)
    if args.cpu:
        args.cuda = False
    elif args.cuda:
        torch.cuda.manual_seed(args.seed)

    args = vars(args)
    print("Running lemmatizer in {} mode".format(args['mode']))

    if args['mode'] == 'train':
        train(args)
    else:
        evaluate(args)

def train(args):
    # load data
    print("[Loading data with batch size {}...]".format(args['batch_size']))
    doc, metasentences = CoNLL.conll2dict(input_file=args['train_file'])
    train_doc = Document(doc, metasentences=metasentences)
    train_batch = DataLoader(train_doc, args['batch_size'], args, evaluation=False)
    vocab = train_batch.vocab
    args['vocab_size'] = vocab['char'].size
    args['pos_vocab_size'] = vocab['pos'].size
    doc, metasentences = CoNLL.conll2dict(input_file=args['eval_file'])
    dev_doc = Document(doc, metasentences=metasentences)
    dev_batch = DataLoader(dev_doc, args['batch_size'], args, vocab=vocab, evaluation=True)

    utils.ensure_dir(args['model_dir'])
    model_file = '{}/{}_lemmatizer.pt'.format(args['model_dir'], args['lang'])

    # pred and gold path
    system_pred_file = args['output_file']
    gold_file = args['gold_file']

    utils.print_config(args)

    # skip training if the language does not have training or dev data
    if len(train_batch) == 0 or len(dev_batch) == 0:
        print("[Skip training because no data available...]")
        sys.exit(0)

    # start training
    # train a dictionary-based lemmatizer
    trainer = Trainer(args=args, vocab=vocab, use_cuda=args['cuda'])
    print("[Training dictionary-based lemmatizer...]")
    dict = train_batch.doc.get([TEXT, XPOS, LEMMA])
    dict = [(e[0].lower(), e[1], e[2]) for e in dict]
    if args.get('external_dict', None) is not None:
        extra_dict = []
        for line in open(args['external_dict']):
            word, lemma, xpos = line.rstrip('\r\n').split('\t')
            extra_dict.append((word.lower(), xpos, lemma))
            dict = extra_dict + dict
    trainer.train_dict(dict)
    print("Evaluating on dev set...")
    dev_preds = trainer.predict_dict([(e[0].lower(), e[1]) for e in dev_batch.doc.get([TEXT, XPOS])])
    dev_batch.doc.set([LEMMA], dev_preds)
    CoNLL.dict2conll(dev_batch.doc.to_dict(), system_pred_file)
    _, _, dev_f = scorer.score(system_pred_file, gold_file)
    print("Dev F1 = {:.2f}".format(dev_f * 100))

    if args.get('dict_only', False):
        # save dictionaries
        trainer.save(model_file)
    else:
        # train a seq2seq model
        print("[Training seq2seq-based lemmatizer...]")
        global_step = 0
        max_steps = len(train_batch) * args['num_epoch']
        dev_score_history = []
        best_dev_preds = []
        current_lr = args['lr']
        global_start_time = time.time()
        format_str = '{}: step {}/{} (epoch {}/{}), loss = {:.6f} ({:.3f} sec/batch), lr: {:.6f}'

        # start training
        for epoch in range(1, args['num_epoch']+1):
            train_loss = 0
            for i, batch in enumerate(train_batch):
                start_time = time.time()
                global_step += 1
                loss = trainer.update(batch, eval=False) # update step
                train_loss += loss
                if global_step % args['log_step'] == 0:
                    duration = time.time() - start_time
                    print(format_str.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), global_step,\
                            max_steps, epoch, args['num_epoch'], loss, duration, current_lr))

            # eval on dev
            print("Evaluating on dev set...")
            dev_preds = []
            dev_edits = []

            dict_preds = trainer.predict_dict([(e[0].lower(), e[1]) for e in dev_batch.doc.get([TEXT, XPOS])])
            # for i, batch in enumerate(dev_batch):
            #     preds, edits = trainer.predict(batch, args['beam_size'])
            #     dev_preds += preds
            #     if edits is not None:
            #         dev_edits += edits
            # dev_preds = trainer.postprocess(dev_batch.doc.get([TEXT]), dev_preds, edits=dev_edits)

            # try ensembling with dict if necessary
            if args.get('ensemble_dict', False):
                skip = trainer.skip_seq2seq([(e[0].lower(), e[1]) for e in dev_batch.doc.get([TEXT, XPOS])])
                doc, metasentences = CoNLL.conll2dict(input_file=args['eval_file'])
                dev_doc = Document(doc, metasentences=metasentences)
                seq2seq_batch = DataLoader(dev_doc, args['batch_size'], args, vocab=vocab, evaluation=True, skip=skip)
                # print("[Ensembling dict with seq2seq model...]")
                # dev_preds = trainer.ensemble(dev_batch.doc.get([TEXT, UPOS]), dev_preds)
            else:
                seq2seq_batch = dev_batch

            if args.get('ensemble_dict', False):
                dev_preds = trainer.postprocess([x for x, y in zip(dev_batch.doc.get([TEXT]), skip) if not y], dev_preds, edits=dev_edits)
                print("[Ensembling dict with seq2seq lemmatizer...]")
                i = 0
                preds1 = []
                for s in skip:
                    if s:
                        preds1.append('')
                    else:
                        preds1.append(dev_preds[i])
                        i += 1
                dev_preds = trainer.ensemble([(e[0].lower(),e[1]) for e in dev_batch.doc.get([TEXT, XPOS])], preds1)
            else:
                dev_preds = trainer.postprocess(dev_batch.doc.get([TEXT]), dev_preds, edits=dev_edits)


            dev_batch.doc.set([LEMMA], dev_preds)
            CoNLL.dict2conll(dev_batch.doc.to_dict(), system_pred_file)
            _, _, dev_score = scorer.score(system_pred_file, gold_file)

            train_loss = train_loss / train_batch.num_examples * args['batch_size'] # avg loss per batch
            print("epoch {}: train_loss = {:.6f}, dev_score = {:.4f}".format(epoch, train_loss, dev_score))

            # save best model
            if epoch == 1 or dev_score > max(dev_score_history):
                trainer.save(model_file)
                print("new best model saved.")
                best_dev_preds = dev_preds

            # lr schedule
            if epoch > args['decay_epoch'] and dev_score <= dev_score_history[-1] and \
                    args['optim'] in ['sgd', 'adagrad']:
                current_lr *= args['lr_decay']
                trainer.update_lr(current_lr)

            dev_score_history += [dev_score]
            print("")

        print("Training ended with {} epochs.".format(epoch))

        best_f, best_epoch = max(dev_score_history)*100, np.argmax(dev_score_history)+1
        print("Best dev F1 = {:.2f}, at epoch = {}".format(best_f, best_epoch))

def evaluate(args):
    # file paths
    system_pred_file = args['output_file']
    gold_file = args['gold_file']
    model_file = '{}/{}.pt'.format(args['model_dir'], args['model_file'])

    # load model
    use_cuda = args['cuda'] and not args['cpu']
    trainer = Trainer(model_file=model_file, use_cuda=use_cuda)
    loaded_args, vocab = trainer.args, trainer.vocab

    for k in args:
        if k.endswith('_dir') or k.endswith('_file') or k in ['shorthand']:
            loaded_args[k] = args[k]

    # laod data
    print("Loading data with batch size {}...".format(args['batch_size']))
    doc, metasentences = CoNLL.conll2dict(input_file=args['eval_file'])
    doc = Document(doc, metasentences=metasentences)
    batch = DataLoader(doc, args['batch_size'], loaded_args, vocab=vocab, evaluation=True)

    # skip eval if dev data does not exist
    if len(batch) == 0:
        print("Skip evaluation because no dev data is available...")
        print("Lemma score:")
        print("{} ".format(args['lang']))
        sys.exit(0)

    dict_preds = trainer.predict_dict([(e[0].lower(),e[1]) for e in batch.doc.get([TEXT, XPOS])])

    if loaded_args.get('dict_only', False):
        preds = dict_preds
    else:
        if loaded_args.get('ensemble_dict', False):
            skip = trainer.skip_seq2seq([(e[0].lower(),e[1]) for e in batch.doc.get([TEXT, XPOS])])
            doc, metasentences = CoNLL.conll2dict(input_file=args['eval_file'])
            dev_doc = Document(doc, metasentences=metasentences)
            seq2seq_batch = DataLoader(dev_doc, args['batch_size'], loaded_args, vocab=vocab, evaluation=True, skip=skip)
        else:
            seq2seq_batch = batch
        print("Running the seq2seq model...")
        preds = []
        edits = []
        for i, b in enumerate(seq2seq_batch):
            ps, es = trainer.predict(b, args['beam_size'])
            preds += ps
            if es is not None:
                edits += es
        # preds = trainer.postprocess(batch.doc.get([TEXT]), preds, edits=edits)

        if loaded_args.get('ensemble_dict', False):
            preds = trainer.postprocess([x for x, y in zip(batch.doc.get([TEXT]), skip) if not y], preds,
                                        edits=edits)
            print("[Ensembling dict with seq2seq lemmatizer...]")
            i = 0
            preds1 = []
            for s in skip:
                if s:
                    preds1.append('')
                else:
                    preds1.append(preds[i])
                    i += 1
            preds = trainer.ensemble([(e[0].lower(), e[1]) for e in batch.doc.get([TEXT, XPOS])], preds1)
        else:
            preds = trainer.postprocess(batch.doc.get([TEXT]), preds, edits=edits)
            print("[Ensembling dict with seq2seq lemmatizer...]")
            # preds = trainer.ensemble(batch.doc.get([TEXT, UPOS]), preds)

    # write to file and score
    batch.doc.set([LEMMA], preds)
    CoNLL.dict2conll(batch.doc.to_dict(), system_pred_file)
    if gold_file is not None:
        _, _, score = scorer.score(system_pred_file, gold_file)

        print("Lemma score:")
        print("{} {:.2f}".format(args['lang'], score*100))

if __name__ == '__main__':
    main()
