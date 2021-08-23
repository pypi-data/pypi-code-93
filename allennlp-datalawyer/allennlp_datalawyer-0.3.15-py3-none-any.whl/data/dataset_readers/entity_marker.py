import re

from typing import List

from allennlp.data.tokenizers import Tokenizer

from transformers import BertTokenizer


class EntityMarker:
    """Converts raw text to BERT-input ids and finds entity position.

    Attributes:
        tokenizer: Bert-base tokenizer.
        h_pattern: A regular expression pattern -- * h *. Using to replace head entity mention.
        t_pattern: A regular expression pattern -- ^ t ^. Using to replace tail entity mention.
        err: Records the number of sentences where we can't find head/tail entity normally.
    """

    def __init__(self, tokenizer: Tokenizer = None):
        self.tokenizer = tokenizer
        self.h_pattern = re.compile(r"\* h \*")
        self.t_pattern = re.compile(r"\^ t \^")
        self.err = 0

    def tokenize_raw(self, raw_text: List[str], head_position: List[int], tail_position: List[int]) -> List[str]:
        tokens = []
        h_mention = []
        t_mention = []
        for i, token in enumerate(raw_text):
            if head_position[0] <= i < head_position[-1]:
                if i == head_position[0]:
                    tokens += ['*', 'h', '*']
                h_mention.append(token)
                continue
            if tail_position[0] <= i < tail_position[-1]:
                if i == tail_position[0]:
                    tokens += ['^', 't', '^']
                t_mention.append(token)
                continue
            tokens.append(token)
        text = " ".join(tokens)
        h_mention = " ".join(h_mention)
        t_mention = " ".join(t_mention)

        # try:
        text = self.h_pattern.sub("[unused1] " + h_mention.replace("\\", r'\\') + " [unused2]", text).replace(r'\\',
                                                                                                              "\\")
        text = self.t_pattern.sub("[unused3] " + t_mention.replace("\\", r'\\') + " [unused4]", text).replace(r'\\',
                                                                                                              "\\")
        # except BaseException as e:
        #     print(e)

        return text.split()

    def tokenize(self, tokenized_sentence: List[str], head_position: List[int], tail_position: List[int]):
        tokens: List[str] = []
        h_mention = []
        t_mention = []
        for i, single_token in enumerate(tokenized_sentence):
            token = single_token
            if head_position[0] <= i < head_position[-1]:
                if i == head_position[0]:
                    tokens += ['*', 'h', '*']
                h_mention.append(token)
                continue
            if tail_position[0] <= i < tail_position[-1]:
                if i == tail_position[0]:
                    tokens += ['^', 't', '^']
                t_mention.append(token)
                continue
            tokens.append(token)

        # tokenize
        tokenized_text = tokens
        tokenized_head = h_mention
        tokenized_tail = t_mention

        p_text = " ".join(tokenized_text)
        p_head = " ".join(tokenized_head)
        p_tail = " ".join(tokenized_tail)

        p_text = self.h_pattern.sub("[unused1] " + p_head + " [unused2]", p_text)
        p_text = self.t_pattern.sub("[unused3] " + p_tail + " [unused4]", p_text)

        f_text = "[CLS] " + p_text + " [SEP]"
        f_text_tokens = f_text.split()
        # If h_pos_li and t_pos_li overlap, we can't find head entity or tail entity.
        try:
            h_pos = f_text_tokens.index("[unused1]")
        except:
            self.err += 1
            h_pos = 0
        try:
            t_pos = f_text_tokens.index("[unused3]")
        except:
            self.err += 1
            t_pos = 0

        tokenized_input = self.tokenizer.tokenize(p_text)
        return tokenized_input, h_pos, t_pos
