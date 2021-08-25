import re
import string


class Punc_remover():

    def __init__(self):

        self.punctuation_list = []
        self.punctuations = r')(}{:؟!،؛»«.' + r"/<>?.,:;"
        self.punctuations = '[' + self.punctuations + '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~' + ']'
        self.pattern = '\s*' + self.punctuations + '+' + '\s*'

    def normalize(self, doc_string):
        normalized_string = self.convert_punctuation(text_line=doc_string)

        return normalized_string

    def convert_punctuation(self, text_line):

        text_line = re.sub(self.pattern, " ", text_line)

        return text_line
