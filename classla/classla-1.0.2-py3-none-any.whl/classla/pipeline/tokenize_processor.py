"""
Processor for performing tokenization
"""

import io
import logging
import os

from classla.pipeline._constants import *
from classla.pipeline.processor import UDProcessor, register_processor
from classla.utils.conll import CoNLL
from classla.utils.obeliks import ObeliksTrainer
from classla.models.common import doc
from classla.utils.reldi import ReldiTrainer

logger = logging.getLogger('classla')

# class for running the tokenizer
@register_processor(name=TOKENIZE)
class TokenizeProcessor(UDProcessor):

    # set of processor requirements this processor fulfills
    PROVIDES_DEFAULT = set([TOKENIZE])
    # set of processor requirements for this processor
    REQUIRES_DEFAULT = set([])
    # default max sequence length
    MAX_SEQ_LENGTH_DEFAULT = 1000

    def _set_up_model(self, config, use_gpu):
        # set up trainer
        if os.path.basename(config['library']) == 'obeliks':
            self._tokenizer = ObeliksTrainer(config.get('lang'), config.get('type'), 'pos' in [el[0] for el in self.pipeline.load_list])
        elif os.path.basename(config['library']) == 'reldi':
            self._tokenizer = ReldiTrainer(config.get('lang'), config.get('type'))
        else:
            raise Exception(f'Tokenizer {config["library"]} not available.')

        if config.get('pretokenized'):
            self._trainer = None

    def process_pre_tokenized_text(self, input_src):
        """
        Pretokenized text can be provided in 2 manners:

        1.) str, tokenized by whitespace, sentence split by newline
        2.) list of token lists, each token list represents a sentence

        generate dictionary data structure
        """

        document = []
        if isinstance(input_src, str):
            sentences = [sent.strip().split() for sent in input_src.strip().split('\n') if len(sent.strip()) > 0]
        elif isinstance(input_src, list):
            sentences = input_src
        idx = 0
        for sentence in sentences:
            sent = []
            for token_id, token in enumerate(sentence):
                sent.append({doc.ID: (token_id + 1, ), doc.TEXT: token, doc.MISC: f'start_char={idx}|end_char={idx + len(token)}'})
                idx += len(token) + 1
            document.append(sent)
        raw_text = ' '.join([' '.join(sentence) for sentence in sentences])
        return raw_text, document

    def process_pre_tokenized_conllu_text(self, input_src):
        """
        Pretokenized text in this case is provided in conllu format.
        """

        return CoNLL.conll2dict(input_str=input_src, generate_raw_text=True)

    def process(self, document):
        assert isinstance(document, str) or (self.config.get('pretokenized') or self.config.get('no_ssplit', False)), \
            "If neither 'pretokenized' or 'no_ssplit' option is enabled, the input to the TokenizerProcessor must be a string."

        if self.config.get('pretokenized'):
            if self.config.get('pretokenized') == 'conllu':
                document, metadocument, raw_text = self.process_pre_tokenized_conllu_text(document)
            else:
                raw_text, document = self.process_pre_tokenized_text(document)
                metadocument = None
        elif hasattr(self, '_variant'):
            return self._variant.process(document)
        else:
            raw_text, document, metadocument = self._tokenizer.tokenize(document)
        return doc.Document(document, raw_text, metasentences=metadocument)
