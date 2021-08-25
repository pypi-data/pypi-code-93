from re import sub
import os
from .tokenizer import Tokenizer
from .data_helper import DataHelper
from .token_merger import ClassifierChunkParser
import re
from .stemmer import FindStems
import json


class AffixNorm():

    def __init__(self, config_file=os.path.dirname(os.path.realpath(__file__)) + "/config/affix.json",
                 double_postfix_joint=True,
                 statistical_space_correction=False,
                 train_file_path="resource/tokenizer/Bijan_khan_chunk.txt",
                 token_merger_path="resource/tokenizer/TokenMerger.pckl",
                 ):
        self.dir_path = os.path.dirname(os.path.realpath(__file__)) + "/"
        self.double_postfix_joint = double_postfix_joint
        self.statistical_space_correction = statistical_space_correction

        with open(config_file) as f:
            self.affix_list = json.load(f)

        self.data_helper = DataHelper()
        self.token_merger = ClassifierChunkParser()

        self.tokenizer = Tokenizer()
        self.stemmer = FindStems(config_file=config_file, double_postfix_joint=self.double_postfix_joint)

        if self.statistical_space_correction:
            self.token_merger_path = self.dir_path + token_merger_path
            self.train_file_path = train_file_path

            if os.path.isfile(self.token_merger_path):
                self.token_merger_model = self.data_helper.load_var(self.token_merger_path)
            elif os.path.isfile(self.train_file_path):
                self.token_merger_model = self.token_merger.train_merger(self.train_file_path, test_split=0)
                self.data_helper.save_var(self.token_merger_path, self.token_merger_model)

    def space_correction(self, doc_string):

        a00 = r'^(' + "|".join(self.affix_list["space_jointer_to_next"]) + r')( )'
        b00 = r'\1‌'
        c00 = sub(a00, b00, doc_string)
        a0 = r'( )(' + "|".join(self.affix_list["space_jointer_to_next"]) + r')( )'
        b0 = r'\1\2‌'
        c0 = sub(a0, b0, c00)
        a1 = r'( )(' + "|".join(self.affix_list["space_jointer_to_previous"]) + r')( )'
        b1 = r'‌\2\3'
        c1 = sub(a1, b1, c0)
        a2 = r'( )' + "|".join(self.affix_list["space_jointer_to_next_previous"]) + r'( )'
        b2 = r'‌\2‌'
        c2 = sub(a2, b2, c1)
        a3 = r'( )(' + "|".join(self.affix_list["space_jointer_to_previous_plus"]) + r')( )'
        b3 = r'‌\2\3'
        c3 = sub(a3, b3, c2)
        return c3

    def normalize(self, doc_string):

        doc_string = self.space_correction(doc_string)

        normalized_string = self.convert_space(text_line=doc_string)

        return normalized_string

    def convert_space(self, text_line):
        text_line_list = text_line.split()

        text = ' '
        for word in text_line_list:
            result = self.stemmer.convert_to_stem(word)
            text += result + ' '

        text = re.sub(r' +', ' ', text)
        return "".join(text.rstrip().lstrip())
