from num2fawords import words
import re
from datetime import datetime
import random


class Time2String:

    def __init__(self):

        self.time_rules = r'( ([0-1]?[0-9]|2[0-3])( +)?:( +)?[0-5]?[0-9](( +)?:( +)?[0-5]?[0-9])?) | (([0-5]?[0-9])' \
                          r'( +)?:( +)?([0-5]?[0-9]) )'
        self.time_format = ['%H:%M:%S', '%H:%M', '%M:%S']
        self.minute_dictionary = {15: "ربع", 30: "نیم"}

    def normalize(self, doc_string):

        normalized_string = self.find_time_part(text_line=doc_string)

        normalized_string = re.sub(r" +", " ", normalized_string)

        return normalized_string

    def find_time_part(self, text_line=""):

        content_new = re.sub(self.time_rules, lambda x: self.time_digit2string(x.group()), " " + text_line + " ")

        return content_new

    def minute_converter(self, time):
        # randomly convert 30,15 to نیم /ربع

        rnd = random.choices([1, 2], weights=(0.6, 0.4), k=1)
        if rnd[0] == 2 and time.second == 0:
            return self.minute_dictionary[time.minute]

        return words(time.minute) + " دقیقه"

    def time_digit2string(self, input_time):

        input_time = re.sub(" ", "", input_time)

        for form in self.time_format:
            try:
                d = datetime.strptime(input_time, form)

                hour = words(d.hour) + " و " if words(d.hour) != "صفر" else ""
                minute = words(d.minute) + " دقیقه" if d.minute not in [15, 30] else self.minute_converter(d)
                second = "و " + words(d.second) + " ثانیه " if str(words(d.second)) != 'صفر' else ''

                return " " + hour + " " + minute + " " + second

            except ValueError:

                continue

        return " " + input_time + " "
