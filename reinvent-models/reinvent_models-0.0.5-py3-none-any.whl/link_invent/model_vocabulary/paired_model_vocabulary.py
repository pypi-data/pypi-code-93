from typing import List

from reinvent_models.link_invent.model_vocabulary.vocabulary import SMILESTokenizer, Vocabulary
from reinvent_models.link_invent.model_vocabulary.model_vocabulary import ModelVocabulary


class PairedModelVocabulary:
    def __init__(self, input_vocabulary: Vocabulary, input_tokenizer: SMILESTokenizer,
                 output_vocabulary: Vocabulary, output_tokenizer: SMILESTokenizer):
        self.input = ModelVocabulary(input_vocabulary, input_tokenizer)
        self.output = ModelVocabulary(output_vocabulary, output_tokenizer)

    def len(self):
        """
        Returns the lenth of both encoder and decoder vocabulary in a tuple

        :return: len(input_vocabulary), len(output_vocabulary)

        """
        return self.input.len(), self.output.len()

    @classmethod
    def from_lists(cls, input_smiles_list: List[str], target_smiles_list: List[str]):
        input_vocabulary = ModelVocabulary.from_list(input_smiles_list)
        output_vocabulary = ModelVocabulary.from_list(target_smiles_list)

        return PairedModelVocabulary(input_vocabulary.vocabulary, input_vocabulary.tokenizer,
                                     output_vocabulary.vocabulary, output_vocabulary.tokenizer)
