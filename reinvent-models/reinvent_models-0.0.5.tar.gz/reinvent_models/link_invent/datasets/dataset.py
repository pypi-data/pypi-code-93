# coding=utf-8
from typing import List, Tuple

import torch
import torch.utils.data as tud
from torch import Tensor
from torch.nn.utils.rnn import pad_sequence

from reinvent_models.link_invent.model_vocabulary.model_vocabulary import ModelVocabulary

#TODO: See where is this class used
class Dataset(tud.Dataset):
    """Dataset that takes a list of SMILES only."""

    def __init__(self, smiles_list, model_vocabulary: ModelVocabulary):
        """
        Instantiates a Dataset.
        :param smiles_list: A list with SMILES strings.
        :param model_vocabulary: A ModelVocabulary object.
        :return:
        """
        self._vocabulary = model_vocabulary.vocabulary
        self._tokenizer = model_vocabulary.tokenizer

        self._encoded_list = []
        for smi in smiles_list:
            tokenized = self._tokenizer.tokenize(smi)
            enc = self._vocabulary.encode(tokenized)

            if enc is not None:
                self._encoded_list.append(enc)

    def __getitem__(self, i):
        return torch.tensor(self._encoded_list[i], dtype=torch.long)  # pylint: disable=E1102

    def __len__(self):
        return len(self._encoded_list)

    @classmethod
    def collate_fn(cls, encoded_seqs):
        return cls.pad_batch(encoded_seqs)

    @staticmethod
    def pad_batch(encoded_seqs: List) -> Tuple[Tensor,Tensor]:
        """
        Pads a batch.
        :param encoded_seqs: A list of encoded sequences.
        :return: A tensor with the sequences correctly padded.
        """
        seq_lengths = torch.tensor([len(seq) for seq in encoded_seqs], dtype=torch.int64)
        return pad_sequence(encoded_seqs, batch_first=True).cuda(), seq_lengths



