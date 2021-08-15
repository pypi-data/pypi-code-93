from re import sub
import string
import re
import json
import os


class CharNormalizer():

    def __init__(self, config_file):
        self.punctuations = r')(}{:؟!،؛»«.' + r"/<>?.,:;"
        self.punctuations = '[' + self.punctuations + string.punctuation + ']'
        self.punctuations = self.punctuations.replace("@", "")
        self.pattern = '\s*' + self.punctuations + '+' + '\s*'

        self.dir_path = os.path.dirname(os.path.realpath(__file__)) + "/"

        with open(config_file) as f:
            mapper_tmp = json.load(f)
        self.char_mapper = {}
        for i in mapper_tmp['Mapper']:
            self.char_mapper.update(mapper_tmp['Mapper'][i])

        self.rule = "|".join(self.char_mapper.keys())
        self.rule = r"(" + self.rule + r")"

    def sub_alphabets(self, doc_string):
        text = re.sub(self.rule, lambda m: self.char_mapper.get(str(m.group()), str(m.group())), str(doc_string))
        return text

    def normalize(self, doc_string):
        doc_string = re.sub(self.pattern, self.add_space, doc_string)

        normalized_string = self.sub_alphabets(doc_string)

        return normalized_string

    def add_space(self, mystring):
        mystring = mystring.group()  # this method return the string matched by re
        mystring = mystring.strip(' ')  # ommiting the whitespace around the pucntuation
        mystring = " " + mystring + " "  # adding a space after and before punctuation
        return mystring
