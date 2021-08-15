from num2fawords import words
import re


class Num2String():

    def __init__(self):
        self.number_rules = r'( +| -| )(((\d{1,30})?[./]\d{1,30} )|(\d{1,30} ))'

    def normalize(self, doc_string):
        normalized_string = self.find_number_part(text_line=doc_string)

        return normalized_string

    def find_number_part(self, text_line):
        text_line = " " + text_line + " "

        content_new = re.sub(self.number_rules, lambda x: self.number_converter(x.group()), text_line)
        content_new = re.sub(' +', ' ', content_new)
        return content_new.lstrip().strip()

    def number_converter(self, input_data):

        try:
            return " " + words(input_data, positive='', negative='منهای ', fraction_separator=' ممیز ',
                               ordinal_denominator=False, decimal_separator=' ممیز ') + " "

        except ValueError:
            return input_data
