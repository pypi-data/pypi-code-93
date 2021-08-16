
import os
import json
import re


class Word_Mapper:

    def __init__(self, config_file=os.path.dirname(os.path.realpath(__file__)) + "/config/word_mappings.json",
                 half_space_char='\u200c'
                 ):
        with open(config_file) as f:
            self.dictionary_mapping = json.load(f)

        self.half_space_char = half_space_char
        self.rule = "|".join(self.dictionary_mapping.keys())
        self.rule = r"(?<!\w)(" + self.rule + r")(?!\w)"

    def normalize(self, doc_string):
        text = re.sub(self.rule, lambda m: self.dictionary_mapping.get(str(m.group()), str(m.group())), str(doc_string))

        text = re.sub(r"\u200c", self.half_space_char, text)
        text = re.sub(r' +', ' ', text)

        return "".join(text.rstrip().lstrip())
