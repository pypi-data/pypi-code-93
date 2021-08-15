from re import sub
import copy
import os
from .tokenizer import Tokenizer
from .data_helper import DataHelper
from .token_merger import ClassifierChunkParser
from num2fawords import words, ordinal_words
import re
from datetime import datetime
import random
import mofid_normalizer.stemmer
import nltk.corpus
import string

from num2fawords import words as internal_words


class Normalizer():

    def __init__(self,
                 half_space_char='\u200c',
                 statistical_space_correction=False,
                 date_normalizing_needed=False,
                 time_normalizing_nedded=False,
                 number_normalizing_needed=False,
                 pinglish_conversion_needed=False,
                 punctuation_normalizing_needed=False,
                 abbreviation_needed=False,
                 upper_case=False,
                 space_normalizing_needed=True,
                 train_file_path="resource/tokenizer/Bijan_khan_chunk.txt",
                 token_merger_path="resource/tokenizer/TokenMerger.pckl"):
        self.dir_path = os.path.dirname(os.path.realpath(__file__)) + "/"
        self.dic1_path =self.dir_path +'resource/normalizer/Dic1_new.txt'
        self.dic2_path =self.dir_path +'resource/normalizer/Dic2_new.txt'
        self.dic3_path =self.dir_path +'resource/normalizer/Dic3_new.txt'
        self.dic1 = self.load_dictionary(self.dic1_path)
        self.dic2 = self.load_dictionary(self.dic2_path)
        self.dic3 = self.load_dictionary(self.dic3_path)

        self.upper_case = upper_case
        self.statistical_space_correction = statistical_space_correction
        self.date_normalizing_needed = date_normalizing_needed
        self.punctuation_normalizing_needed = punctuation_normalizing_needed
        self.time_normalizing_needed = time_normalizing_nedded
        self.number_normalizing_needed = number_normalizing_needed
        self.space_normalizing_needed = space_normalizing_needed
        self.punctuation_normalizing_needed = punctuation_normalizing_needed
        self.abbreviation_needed = abbreviation_needed
        self.pinglish_conversion_needed = pinglish_conversion_needed
        self.data_helper = DataHelper()
        self.token_merger = ClassifierChunkParser()

        if self.date_normalizing_needed or self.pinglish_conversion_needed or self.time_normalizing_needed or self.number_normalizing_needed or self.abbreviation_needed or self.punctuation_normalizing_needed or self.space_normalizing_needed:
            self.tokenizer = Tokenizer()
            self.date_normalizer = DateNormalizer()
            self.time_normalizer = TimeNormalizer()
            self.pinglish_conversion = PinglishNormalizer()
            self.number_normalizer = NumberNormalizer()
            self.abbreviation_normalizer = AbbreviationNormalizer()
            self.punctuation_normalizer = Punctuation()
            self.space_normalizer = Spacenormalizer()

        if self.statistical_space_correction:
            self.token_merger_path = self.dir_path + token_merger_path
            self.train_file_path = train_file_path
            self.half_space_char = half_space_char

            if os.path.isfile(self.token_merger_path):
                self.token_merger_model = self.data_helper.load_var(self.token_merger_path)
            elif os.path.isfile(self.train_file_path):
                self.token_merger_model = self.token_merger.train_merger(self.train_file_path, test_split=0)
                self.data_helper.save_var(self.token_merger_path, self.token_merger_model)

    def load_dictionary(self, file_path):
        dict = {}
        with open(file_path, 'r', encoding='utf-8') as f:
            g = f.readlines()
            for Wrds in g:
                wrd = Wrds.split(' ')
                dict[wrd[0].strip()] = sub('\n', '', wrd[1].strip())
        return dict

    def sub_alphabets(self, doc_string):

        # try:
        #     doc_string = doc_string.decode('utf-8')
        # except UnicodeEncodeError:
        #     pass
        a0 = "ء"
        b0 = "ئ"
        c0 = sub(a0, b0, doc_string)
        a1 = r"ٲ|ٱ|إ|ﺍ|أ"
        a11 = r"ﺁ|آ"
        b1 = r"ا"
        b11 = r"آ"
        c11 = sub(a11, b11, c0)
        c1 = sub(a1, b1, c11)
        a2 = r"ﺐ|ﺏ|ﺑ"
        b2 = r"ب"
        c2 = sub(a2, b2, c1)
        a3 = r"ﭖ|ﭗ|ﭙ|ﺒ|ﭘ"
        b3 = r"پ"
        c3 = sub(a3, b3, c2)
        a4 = r"ﭡ|ٺ|ٹ|ﭞ|ٿ|ټ|ﺕ|ﺗ|ﺖ|ﺘ"
        b4 = r"ت"
        c4 = sub(a4, b4, c3)
        a5 = r"ﺙ|ﺛ"
        b5 = r"ث"
        c5 = sub(a5, b5, c4)
        a6 = r"ﺝ|ڃ|ﺠ|ﺟ"
        b6 = r"ج"
        c6 = sub(a6, b6, c5)
        a7 = r"ڃ|ﭽ|ﭼ"
        b7 = r"چ"
        c7 = sub(a7, b7, c6)
        a8 = r"ﺢ|ﺤ|څ|ځ|ﺣ"
        b8 = r"ح"
        c8 = sub(a8, b8, c7)
        a9 = r"ﺥ|ﺦ|ﺨ|ﺧ"
        b9 = r"خ"
        c9 = sub(a9, b9, c8)
        a10 = r"ڏ|ډ|ﺪ|ﺩ"
        b10 = r"د"
        c10 = sub(a10, b10, c9)
        a11 = r"ﺫ|ﺬ|ﻧ"
        b11 = r"ذ"
        c11 = sub(a11, b11, c10)
        a12 = r"ڙ|ڗ|ڒ|ڑ|ڕ|ﺭ|ﺮ"
        b12 = r"ر"
        c12 = sub(a12, b12, c11)
        a13 = r"ﺰ|ﺯ"
        b13 = r"ز"
        c13 = sub(a13, b13, c12)
        a14 = r"ﮊ"
        b14 = r"ژ"
        c14 = sub(a14, b14, c13)
        a15 = r"ݭ|ݜ|ﺱ|ﺲ|ښ|ﺴ|ﺳ"
        b15 = r"س"
        c15 = sub(a15, b15, c14)
        a16 = r"ﺵ|ﺶ|ﺸ|ﺷ"
        b16 = r"ش"
        c16 = sub(a16, b16, c15)
        a17 = r"ﺺ|ﺼ|ﺻ"
        b17 = r"ص"
        c17 = sub(a17, b17, c16)
        a18 = r"ﺽ|ﺾ|ﺿ|ﻀ"
        b18 = r"ض"
        c18 = sub(a18, b18, c17)
        a19 = r"ﻁ|ﻂ|ﻃ|ﻄ"
        b19 = r"ط"
        c19 = sub(a19, b19, c18)
        a20 = r"ﻆ|ﻇ|ﻈ"
        b20 = r"ظ"
        c20 = sub(a20, b20, c19)
        a21 = r"ڠ|ﻉ|ﻊ|ﻋ"
        b21 = r"ع"
        c21 = sub(a21, b21, c20)
        a22 = r"ﻎ|ۼ|ﻍ|ﻐ|ﻏ"
        b22 = r"غ"
        c22 = sub(a22, b22, c21)
        a23 = r"ﻒ|ﻑ|ﻔ|ﻓ"
        b23 = r"ف"
        c23 = sub(a23, b23, c22)
        a24 = r"ﻕ|ڤ|ﻖ|ﻗ"
        b24 = r"ق"
        c24 = sub(a24, b24, c23)
        a25 = r"ڭ|ﻚ|ﮎ|ﻜ|ﮏ|ګ|ﻛ|ﮑ|ﮐ|ڪ|ك"
        b25 = r"ک"
        c25 = sub(a25, b25, c24)
        a26 = r"ﮚ|ﮒ|ﮓ|ﮕ|ﮔ"
        b26 = r"گ"
        c26 = sub(a26, b26, c25)
        a27 = r"ﻝ|ﻞ|ﻠ|ڵ"
        b27 = r"ل"
        c27 = sub(a27, b27, c26)
        a28 = r"ﻡ|ﻤ|ﻢ|ﻣ"
        b28 = r"م"
        c28 = sub(a28, b28, c27)
        a29 = r"ڼ|ﻦ|ﻥ|ﻨ"
        b29 = r"ن"
        c29 = sub(a29, b29, c28)
        a30 = r"ވ|ﯙ|ۈ|ۋ|ﺆ|ۊ|ۇ|ۏ|ۅ|ۉ|ﻭ|ﻮ|ؤ"
        b30 = r"و"
        c30 = sub(a30, b30, c29)
        a31 = r"ﺔ|ﻬ|ھ|ﻩ|ﻫ|ﻪ|ۀ|ە|ة|ہ"
        b31 = r"ه"
        c31 = sub(a31, b31, c30)
        a32 = r"ﭛ|ﻯ|ۍ|ﻰ|ﻱ|ﻲ|ں|ﻳ|ﻴ|ﯼ|ې|ﯽ|ﯾ|ﯿ|ێ|ے|ى|ي"
        b32 = r"ی"
        c32 = sub(a32, b32, c31)
        a33 = r'¬'
        b33 = r'‌'
        c33 = sub(a33, b33, c32)
        pa0 = r'•|·|●|·|・|∙|｡|ⴰ'
        pb0 = r'.'
        pc0 = sub(pa0, pb0, c33)
        pa1 = r',|٬|٫|‚|，'
        pb1 = r'،'
        pc1 = sub(pa1, pb1, pc0)
        pa2 = r'ʕ'
        pb2 = r'؟'
        pc2 = sub(pa2, pb2, pc1)
        na0 = r'۰|٠'
        nb0 = r'0'
        nc0 = sub(na0, nb0, pc2)
        na1 = r'۱|١'
        nb1 = r'1'
        nc1 = sub(na1, nb1, nc0)
        na2 = r'۲|٢'
        nb2 = r'2'
        nc2 = sub(na2, nb2, nc1)
        na3 = r'۳|٣'
        nb3 = r'3'
        nc3 = sub(na3, nb3, nc2)
        na4 = r'۴|٤'
        nb4 = r'4'
        nc4 = sub(na4, nb4, nc3)
        na5 = r'۵'
        nb5 = r'۵'
        nc5 = sub(na5, nb5, nc4)
        na6 = r'۶|٦'
        nb6 = r'6'
        nc6 = sub(na6, nb6, nc5)
        na7 = r'۷|٧'
        nb7 = r'7'
        nc7 = sub(na7, nb7, nc6)
        na8 = r'۸|٨'
        nb8 = r'8'
        nc8 = sub(na8, nb8, nc7)
        na9 = r'۹|٩'
        nb9 = r'9'
        nc9 = sub(na9, nb9, nc8)
        ea1 = r'ـ|ِ|ُ|َ|ٍ|ٌ|ً|'
        eb1 = r''
        ec1 = sub(ea1, eb1, nc9)
        Sa1 = r'( )+'
        Sb1 = r' '
        Sc1 = sub(Sa1, Sb1, ec1)
        Sa2 = r'(\n)+'
        Sb2 = r'\n'
        Sc2 = sub(Sa2, Sb2, Sc1)

        return Sc2

    def space_correction(self, doc_string):
        a00 = r'^(بی|می|نمی)( )'
        b00 = r'\1‌'
        c00 = sub(a00, b00, doc_string)
        a0 = r'( )(می|نمی|بی)( )'
        b0 = r'\1\2‌'
        c0 = sub(a0, b0, c00)
        a1 = r'( )(هایی|ها|های|ایی|هایم|هایت|هایش|هایمان|هایتان|هایشان|ات|ان|ین' \
             r'|انی|بان|ام|ای|یم|ید|اید|اند|بودم|بودی|بود|بودیم|بودید|بودند|ست)( )'
        b1 = r'‌\2\3'
        c1 = sub(a1, b1, c0)
        a2 = r'( )(شده|نشده)( )'
        b2 = r'‌\2‌'
        c2 = sub(a2, b2, c1)
        a3 = r'( )(طلبان|طلب|گرایی|گرایان|شناس|شناسی|گذاری|گذار|گذاران|شناسان|گیری|پذیری|بندی|آوری|سازی|' \
             r'بندی|کننده|کنندگان|گیری|پرداز|پردازی|پردازان|آمیز|سنجی|ریزی|داری|دهنده|آمیز|پذیری' \
             r'|پذیر|پذیران|گر|ریز|ریزی|رسانی|یاب|یابی|گانه|گانه‌ای|انگاری|گا|بند|رسانی|دهندگان|دار)( )'
        b3 = r'‌\2\3'
        c3 = sub(a3, b3, c2)
        return c3

    def space_correction_plus1(self, doc_string):
        out_sentences = ''
        for wrd in doc_string.split(' '):
            try:
                out_sentences = out_sentences + ' ' + self.dic1[wrd]
            except KeyError:
                out_sentences = out_sentences + ' ' + wrd
        return out_sentences

    def space_correction_plus2(self, doc_string):
        out_sentences = ''
        wrds = doc_string.split(' ')
        L = wrds.__len__()
        if L < 2:
            return doc_string
        cnt = 1
        for i in range(0, L - 1):
            w = wrds[i] + wrds[i + 1]
            try:
                out_sentences = out_sentences + ' ' + self.dic2[w]
                cnt = 0
            except KeyError:
                if cnt == 1:
                    out_sentences = out_sentences + ' ' + wrds[i]
                cnt = 1
        if cnt == 1:
            out_sentences = out_sentences + ' ' + wrds[i + 1]
        return out_sentences

    def space_correction_plus3(self, doc_string):
        # Dict = {'گفتوگو': 'گفت‌وگو'}
        out_sentences = ''
        wrds = doc_string.split(' ')
        L = wrds.__len__()
        if L < 3:
            return doc_string
        cnt = 1
        cnt2 = 0
        for i in range(0, L - 2):
            w = wrds[i] + wrds[i + 1] + wrds[i + 2]
            try:
                out_sentences = out_sentences + ' ' + self.dic3[w]
                cnt = 0
                cnt2 = 2
            except KeyError:
                if cnt == 1 and cnt2 == 0:
                    out_sentences = out_sentences + ' ' + wrds[i]
                else:
                    cnt2 -= 1
                cnt = 1
        if cnt == 1 and cnt2 == 0:
            out_sentences = out_sentences + ' ' + wrds[i + 1] + ' ' + wrds[i + 2]
        elif cnt == 1 and cnt2 == 1:
            out_sentences = out_sentences + ' ' + wrds[i + 2]
        return out_sentences

    def normalize(self, doc_string, new_line_elimination=False):


        normalized_string = self.sub_alphabets(doc_string)

        # normalized_string = self.data_helper.clean_text(normalized_string, new_line_elimination).strip()

        normalized_string = re.sub(r"\u200c", " ", normalized_string)  # for normalization

        # if self.statistical_space_correction:
        #     token_list = normalized_string.strip().split()
        #     token_list = [x.strip("\u200c") for x in token_list if len(x.strip("\u200c")) != 0]
        #     token_list = self.token_merger.merg_tokens(token_list, self.token_merger_model, self.half_space_char)
        #     normalized_string = " ".join(x for x in token_list)
        #     normalized_string = self.data_helper.clean_text(normalized_string, new_line_elimination)
        #
        # else:
        #     normalized_string = self.space_correction(self.space_correction_plus1(
        #         self.space_correction_plus2(self.space_correction_plus3(normalized_string)))).strip()
        #

        if self.date_normalizing_needed:
            normalized_string = self.date_normalizer.find_date_part(text_line=normalized_string)

        if self.time_normalizing_needed:
            normalized_string = self.time_normalizer.find_time_part(text_line=normalized_string)

        if self.number_normalizing_needed:
            normalized_string = self.number_normalizer.find_number_part(text_line=normalized_string)

        if self.abbreviation_needed:
            normalized_string = self.abbreviation_normalizer.find_abbreviation_part(text_line=normalized_string)

        if self.pinglish_conversion_needed:
            normalized_string = self.pinglish_conversion.pingilish2persian(
                self.tokenizer.tokenize_words(normalized_string))

        if self.punctuation_normalizing_needed:
            normalized_string = self.punctuation_normalizer.convert_punctuation(text_line=normalized_string)

        if self.space_normalizing_needed:
            normalized_string = self.space_normalizer.convert_space(text_line=normalized_string)

        if self.upper_case:
            return normalized_string.upper()

        return normalized_string


class Spacenormalizer():
    def __init__(self):
        pass
        # self.stemmer = mofid_normalizer.stemmer.FindStems()

    def convert_space(self, text_line):
        pass
        # text_line_list = text_line.split()
        #
        # text = ' '
        # for word in text_line_list:
        #     result = self.stemmer.convert_to_stem(word)
        #     text += result + ' '
        #
        # text = re.sub(' +', ' ', text)
        # return "".join(text.rstrip().lstrip())


class Punctuation():
    def __init__(self):
        self.punctuation_list = []

    def convert_punctuation(self, text_line):
        input_data = re.sub("%|٪", 'درصد', text_line)
        input_data = re.sub(r'[^\w\s]', ' ', input_data)
        input_data = re.findall(r'[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FF].*', input_data)

        return ''.join(input_data)

    def persian_converter(self, input_data):
        print(input_data)
        return input_data


class AbbreviationNormalizer():
    def __init__(self):
        self.abbreviation_rules = r'( ه ق )|( ه ش )|( ه.ق )|( ه.ش )|( ع )|( ره )|(\(ه ش\))|(\(ه ق\))|(\(ه.ش\))|(\(ه.ق\))|(\(ره\))|(\(ع\))|( ه ق )|( ه ش )|( ه.ق. )|( ه.ش. )|( ره )|(\(ه ش\))|(\(ه ق\))|(\(.ه.ش\))|(\(ه.ق.\))|(\(ره\))|(\(ع\))'
        self.abbreviation_dictionary = {
            'هق': ' هجری قمری ',
            'هش': ' هجری شمسی ',
            'ره': ' رحمه الله ',
            'ع': ' علیه السلام '
        }

    def find_abbreviation_part(self, text_line):
        content_new = re.sub(self.abbreviation_rules, lambda x: self.abbreviation_converter(x.group()), text_line)

        return content_new

    def abbreviation_converter(self, input_data):
        try:
            return self.abbreviation_dictionary[re.sub('\W+', "", input_data)]
        except:
            return input_data


class TimeNormalizer():
    def __init__(self):

        self.time_rules = r'(([0-1]?[0-9]|2[0-3]):[0-5]?[0-9](:[0-5]?[0-9])?)|(([0-5]?[0-9]):([0-5]?[0-9]) )'
        self.time_format = ['%H:%M:%S', '%H:%M', '%M:%S']
        self.minute_dictionary = {15: "ربع", 30: "نیم"}

    def find_time_part(self, text_line=""):

        content_new = re.sub(self.time_rules, lambda x: self.time_digit2string(x.group()), text_line)

        return content_new

    def minute_converter(self, time):
        # ranodmly convert 30,15 to نیم /ربع

        rnd = random.choices([1, 2], weights=(0.6, 0.4), k=1)
        if rnd[0] == 2 and time.second == 0:
            return self.minute_dictionary[time.minute]

        return words(time.minute) + " دقیقه"

    def time_digit2string(self, input_time):

        for form in self.time_format:
            try:
                d = datetime.strptime(input_time, form)

                hour = words(d.hour) + " و "
                minute = words(d.minute) + " دقیقه" if d.minute not in [15, 30] else self.minute_converter(d)
                second = "و " + words(d.second) + " ثانیه " if str(words(d.second)) != 'صفر' else ''

                return hour + " " + minute + " " + second

            except ValueError:

                continue

        return input_time


class NumberNormalizer():
    def __init__(self):
        self.number_rules = r'( +| -)?(((\d{1,30})?[./]\d{1,30})|(\d{1,20}))'

    def find_number_part(self, text_line):

        content_new = re.sub(self.number_rules, lambda x: self.number_converter((x.group())), text_line)

        return content_new

    def number_converter(self, input_data):

        try:
            return " " + words(input_data, positive='', negative='منهای ', fraction_separator=' تقسیم بر ',
                               ordinal_denominator=False, decimal_separator=' ممیز ') + "  "

        except ValueError:
            return input_data


class DateNormalizer():
    def __init__(self):

        self.month_names = {'شمسی': {1: "فروردین", 2: "اردیبهشت", 3: "خرداد", 4:
            "تیر", 5: "مرداد", 6: "شهریور", 7:
                                         "مهر", 8: "آبان", 9: "آذر", 10:
                                         "دی", 11: "بهمن", 12: "اسفند"},

                            'قمری': {1: "محرم", 2: "صفر", 3: "ربیع‌الاول", 4:
                                "ربیع‌الثانی", 5: "جمادی‌الاول", 6: "جمادی‌الثانی", 7:
                                         "رجب", 8: "شعبان", 9: "رمضان", 10:
                                         "شوال", 11: "ذیقعده", 12: "ذیحجه"},

                            'میلادی': {1: "ژانویه", 2: "فوریه", 3: "مارچ", 4:
                                "آپریل", 5: "می", 6: "جون", 7:
                                           "جولای", 8: "آگوست", 9: "سپتامبر", 10:
                                           "اکتبر", 11: "نوامبر", 12: "دسامبر"}}

        self.num_dict = {"صد": 100, "هزار": 1000, "میلیون": 1000000, "دویست": 200,
                         "ده": 10, "نه": 9, "هشت": 8, "هفت": 7, "شش": 6, "پنج": 5,
                         "چهار": 4, "سه": 3, "دو": 2, "یک": 1, "یازده": 11, "سیزده": 13,
                         "چهارده": 14, "دوازده": 12, "پانزده": 15, "شانزده": 16, "هفده": 17,
                         "هجده": 18, "نوزده": 19, "بیست": 20, "سی": 30, "چهل": 40, "پنجاه": 50,
                         "شصت": 60, "هفتاد": 70, "نود": 90, "سیصد": 300, "چهارصد": 400,
                         "پانصد": 500, "ششصد": 600, "هفتصد": 700, "هشتصد": 800, "نهصد": 900,
                         "هشتاد": 80, " ": 0, "میلیارد": 1000000000,
                         "صدم": 100, "هزارم": 1000, "دویستم": 200,
                         "دهم": 10, "نهم": 9, "هشتم": 8, "هفتم": 7, "ششم": 6, "پنجم": 5,
                         "چهارم": 4, "سوم": 3, "دوم": 2, "یکم": 1, "اول": 1, "یازدهم": 11, "سیزدهم": 13,
                         "چهاردهم": 14, "دوازدهم": 12, "پانزدهم": 15, "شانزدهم": 16, "هفدهم": 17,
                         "هجدهم": 18, "نوزدهم": 19, "بیستم": 20, "چهلم": 40, "پنجاهم": 50,
                         "شصتم": 60, "هفتادم": 70, "نودم": 90, "سیصدم": 300, "چهارصدم": 400,
                         "پانصدم": 500, "ششصدم": 600, "هفتصدم": 700, "هشتصدم": 800, "نهصدم": 900,
                         "هشتادم": 80}

        self.format_list = ['%Y-%m-%d', '%Y-%d-%m', '%d-%m-%Y', '%m-%d-%Y', '%Y/%m/%d', '%Y/%d/%m', '%d/%m/%Y',
                            '%m/%d/%Y']

        self.date_rules = r'(((0[1-9]|1[012]|\b[1-9])[-/.](0[1-9]|[12][0-9]|3[01]|[1-9])[-/.][11-20]\d\d\d)|((0[0-9]|[12][0-9]|3[01]|\b[1-9])[-/.](0[1-9]|1[012]|[1-9])[-/.]([11-20]\d\d\d))|(([11-20]\d\d\d)[-/.](0[1-9]|1[012]|[1-9])[-/.](0[1-9]|[12][0-9]|3[01]|[1-9]\b))|(([11-20]\d\d\d)[-/.](0[1-9]|[12][0-9]|3[01]|[1-9])[-/.](0[1-9]|1[012]|[1-9]\b)))'

    def find_date_part(self, text_line=""):

        content_new = re.sub(self.date_rules, lambda x: self.date_digit2string(x.group()), text_line)

        return content_new

    def convert_month(self, month, date_type):
        rnd = random.choices([1, 2, 3], weights=(0.6, 0.3, 0.1), k=1)

        if rnd[0] == 1: return self.month_names[date_type][month]
        if rnd[0] == 2: return self.month_names[date_type][month] + " ماه "
        if rnd[0] == 3: return str(words(month))

    def convert_year(self, year, date_type):

        rnd = random.choices([1, 2, 3, 4], weights=(0.4, 0.2, 0.1, 0.2), k=1)

        if rnd[0] == 1: return words(year)
        if rnd[0] == 2: return "سال " + words(year)
        if rnd[0] == 3: return "سال " + words(year) + ' ' + date_type
        if rnd[0] == 4: return words(year) + ' ' + date_type

    def convert_day(self, day):
        rnd = random.choices([1, 2], weights=(0.4, 0.6), k=1)

        if rnd[0] == 1: return words(day)
        if rnd[0] == 2: return ordinal_words(day)

    def date_type(self, date):
        if int(date) < 1410:
            return 'شمسی'
        elif 1550 > int(date) > 1410:
            return 'قمری'
        else:
            return 'میلادی'

    def date_digit2string(self, input_date):

        split_date = re.split("-|/|\.", input_date)
        if 1000 < int(split_date[0]) < 3000 and 0 < int(split_date[1]) < 13 and 0 < int(split_date[2]) < 32:

            date_type = self.date_type(int(split_date[0]))

            month = self.convert_month(int(split_date[1]), date_type)
            year = self.convert_year(int(split_date[0]), date_type)
            day = self.convert_day(int(split_date[2]))

            return day + " " + month + " " + year

        elif 1000 < int(split_date[0]) < 3000 and 0 < int(split_date[2]) < 13 and 0 < int(split_date[1]) < 32:

            date_type = self.date_type(int(split_date[0]))

            month = self.convert_month(int(split_date[2]), date_type)
            year = self.convert_year(int(split_date[0]), date_type)
            day = self.convert_day(int(split_date[1]))
            return day + " " + month + " " + year

        elif 1000 < int(split_date[2]) < 3000 and 0 < int(split_date[1]) < 13 and 0 < int(split_date[0]) < 32:

            date_type = self.date_type(int(split_date[2]))

            month = self.convert_month(int(split_date[1]), date_type)
            year = self.convert_year(int(split_date[2]), date_type)
            day = self.convert_day(int(split_date[0]))

            return day + " " + month + " " + year

        elif 1000 < int(split_date[2]) < 3000 and 0 < int(split_date[0]) < 13 and 0 < int(split_date[1]) < 32:

            date_type = self.date_type(int(split_date[2]))

            month = self.convert_month(int(split_date[0]), date_type)
            year = self.convert_year(int(split_date[2]), date_type)
            day = self.convert_day(int(split_date[1]))

            return day + " " + month + " " + year

        else:

            return input_date


class PinglishNormalizer():
    def __init__(self):
        self.data_helper = DataHelper()
        self.file_dir = os.path.dirname(os.path.realpath(__file__)) + "/"

        self.en_dict_filename = self.file_dir + "resource/tokenizer/enDict"
        self.en_dict = self.data_helper.load_var(self.en_dict_filename)

        self.fa_dict_filename = self.file_dir + "resource/tokenizer/faDict"
        self.fa_dict = self.data_helper.load_var(self.fa_dict_filename)

    def pingilish2persian(self, pinglish_words_list):

        for i, word in enumerate(pinglish_words_list):
            if word in self.en_dict:
                pinglish_words_list[i] = self.en_dict[word]  # .decode("utf-8")
                # inp = inp.replace(word, enDict[word], 1)
            else:
                ch = self.characterize(word)
                pr = self.map_char(ch)
                amir = self.make_word(pr)
                for wd in amir:
                    am = self.escalation(wd)
                    asd = ''.join(am)
                    if asd in self.fa_dict:
                        pinglish_words_list[i] = asd  # .decode("utf-8")
                        # inp = inp.replace(word, asd, 1)
        inp = " ".join(x for x in pinglish_words_list)
        return inp

    def characterize(self, word):
        list_of_char = []
        i = 0
        while i < len(word):
            char = word[i]
            sw_out = self.switcher(char)
            if (sw_out == None):
                esp_out = None
                if (i < len(word) - 1):
                    esp_out = self.esp_check(word[i], word[i + 1])
                if (esp_out == None):
                    list_of_char.append(word[i])
                else:
                    list_of_char.append(esp_out)
                    i += 1
            else:
                list_of_char.append(sw_out)
            i += 1
        return list_of_char

    def switcher(self, ch):
        switcher = {
            "c": None,
            "k": None,
            "z": None,
            "s": None,
            "g": None,
            "a": None,
            "u": None,
            "e": None,
            "o": None
        }
        return switcher.get(ch, ch)

    def esp_check(self, char1, char2):
        st = char1 + char2
        if (st == "ch"):
            return "ch"
        elif (st == "kh"):
            return "kh"
        elif (st == "zh"):
            return "zh"
        elif (st == "sh"):
            return "sh"
        elif (st == "gh"):
            return "gh"
        elif (st == "aa"):
            return "aa"
        elif (st == "ee"):
            return "ee"
        elif (st == "oo"):
            return "oo"
        elif (st == "ou"):
            return "ou"
        else:
            return None

    def map_char(self, word):
        listm = []
        sw_out = self.map_switcher(word[0])
        i = 0
        if (sw_out == None):
            listm.append(["ا"])
            i += 1
        if (word[0] == "oo"):
            listm.append(["او"])
            i += 1
        while i < len(word):
            listm.append(self.char_switcher(word[i]))
            i += 1
        if word[len(word) - 1] == "e":
            listm.append(["ه"])
        elif word[len(word) - 1] == "a":
            listm.append(["ا"])
        elif word[len(word) - 1] == "o":
            listm.append(["و"])
        elif word[len(word) - 1] == "u":
            listm.append(["و"])

        return listm

    def map_switcher(self, ch):
        switcher = {
            "a": None,
            "e": None,
            "o": None,
            "u": None,
            "ee": None,

            "ou": None
        }
        return switcher.get(ch, ch)

    def make_word(self, chp):
        word_list = [[]]
        for char in chp:
            word_list_temp = []
            for tmp_word_list in word_list:
                for chch in char:
                    tmp = copy.deepcopy(tmp_word_list)
                    tmp.append(chch)
                    word_list_temp.append(tmp)
            word_list = word_list_temp
        return word_list

    def escalation(self, word):
        tmp = []
        i = 0
        t = len(word)
        while i < t - 1:
            tmp.append(word[i])
            if word[i] == word[i + 1]:
                i += 1
            i += 1
        if i != t:
            tmp.append(word[i])
        return tmp

    def char_switcher(self, ch):
        switcher = {
            'a': ["", "ا"],
            'c': ["ث", "ص", "ص"],
            'h': ["ه", "ح"],
            'b': ["ب"],
            'p': ["پ"],
            't': ["ت", "ط"],
            's': ["س", "ص", "ث"],
            'j': ["ج"],
            'ch': ["چ"],
            'kh': ["خ"],
            'q': ["ق", "غ"],
            'd': ["د"],
            'z': ["ز", "ذ", "ض", "ظ"],
            'r': ["ر"],
            'zh': ["ژ"],
            'sh': ["ش"],
            'gh': [",ق", "غ"],
            'f': ["ف"],
            'k': ["ک"],
            'g': ["گ"],
            'l': ["ل"],
            'm': ["م"],
            'n': ["ن"],
            'v': ["و"],
            'aa': ["ا"],
            'ee': ["ی"],
            'oo': ["و"],
            'ou': ["و"],
            'i': ["ی"],
            'y': ["ی"],
            ' ': [""],
            'w': ["و"],
            'e': ["", "ه"],
            'o': ["", "و"]
        }
        return switcher.get(ch, "")
