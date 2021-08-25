from num2fawords import words, ordinal_words
import re

import random


class Date2String():

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

        self.date_rules = r'(((0[1-9]|1[012]|\b[1-9])( )*[-/.]( )*(0[1-9]|[12][0-9]|3[01]|[1-9])( )*[-/.]( )*[11-20]\d\d\d)|((0[0-9]|[12][0-9]|3[01]|\b[1-9])( )*[-/.]( )*(0[1-9]|1[012]|[1-9])( )*[-/.]( )*([11-20]\d\d\d))|(([11-20]\d\d\d)( )*[-/.]( )*(0[1-9]|1[012]|[1-9])( )*[-/.]( )*(0[1-9]|[12][0-9]|3[01]|[1-9]\b))|(([11-20]\d\d\d)( )*[-/.]( )*(0[1-9]|[12][0-9]|3[01]|[1-9])( )*[-/.]( )*(0[1-9]|1[012]|[1-9]\b)))'

    def normalize(self, doc_string):

        normalized_string = self.find_date_part(text_line=doc_string)

        return normalized_string

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
