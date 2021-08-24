# -*- coding: utf-8 -*-
"""

    Модуль кодирования и декодирования служебных данных
    Правила записи данных в файлах .sd, примеры и комментарии находятся в файле documentation/syntax_of_sd_format.py

"""
import io
import re

version = '2021.08.24-p[3.8]dr-01.012.000'  # year.month.day-version_type-major.minor.patch


# major version number - incompatible with previous versions; minor v.n. - compatibility with p. v.; patch - bag fix
# type version:
# first char: programming language (p-Python)
# bracketed group: Python version [3.8]
# second letter: d - developing version;  w - working prototype version; r - release version; s - stable version;
# third letter: b - bags fixing; c - changes making; p - privat testing; o - open testing; r - ready version;


class ServiceDataConversion:
    """
        Класс кодирования и декодирования служебных данных из словаря Python в формат .sd и наоборот
        Методы класса:
            __init__ - метод инициализации объекта класса
            sd_conversion_management - метод получающий адреса файла формата .sd и возвращающий Python словарь с данными
            self.file_path (str): путь к файлу для его декодирования
            self.request_type (str): тип операции encode или decode
            self.source_dictionary (dict): переданный словарь python, для его кодирования в формат .sd
            self.decoding_result (dict): итоговый словарь python полученный при декодировании .sd файла
            self.execution_result (bool): фиксирование результата выполнения операций True или False
    """

    def __init__(self, file_path, source_dictionary=None):
        """
            Метод инициализации экземпляра класса и вызова метода исполнения
            :param file_path: путь к файлу для его декодирования
            :param source_dictionary: python словарь переданный для кодирования в sd формат
        """
        self.file_path = file_path
        if source_dictionary:
            self.request_type = 'encoding'
        else:
            self.request_type = 'decoding'
        if source_dictionary is None:
            self.source_dictionary = {}
        else:
            self.source_dictionary = source_dictionary
        self.decoding_result = None
        self.execution_result = None
        self.sd_conversion_management()

    def sd_conversion_management(self):
        """
            Метод преобразующий данные из .sd в python (dict) или наоборот
            Используемые переменные:
            source_dictionary: исходный словарь python для его кодирования в формат sd:
            request_type: 'encoding' or 'decoding'
            file_path: адрес файла
            :return: self.execution_result  True or False
        """
        file_path = self.file_path
        request_type = self.request_type
        source_dictionary = self.source_dictionary
        execution_result = self.execution_result

        if request_type == 'encoding':
            try:
                with open(file_path, mode='w', encoding='utf-8') as file:
                    file.write('')
            except FileNotFoundError as e:
                print('FileNotFoundError - Адрес для сохранения указан не верно', format(e))
            if source_dictionary and type(source_dictionary) == dict:
                encoding_obj = SdDataEncoding(file_path, source_dictionary)
                encoding_obj.sd_data_encoding_management()
        elif request_type == 'decoding':
            try:
                with open(file_path, mode='r', encoding='utf-8') as file:
                    decoding_obj = SdDataDecoding(file)
                    self.decoding_result = decoding_obj.sd_data_decoding_management()
            except FileNotFoundError as e:
                print('FileNotFoundError - Адрес *.sd файла указан не верно', format(e))


class SdDataDecoding:
    """
        Класс парсинга данных sd файла и декодирования данных в формат словаря Python

        Методы:
            __init__ - метод инициализации объекта класса
            sd_data_decoding_management - метод запускающий парсинг данных sd файла и управляющий процессом парсинга
            multiline_string_value_parsing - Метод парсинга многострочного значения для ключа первого уровня
            string_parsing_with_triple_quotes - Метод парсинга однострочного значения ключа первого уровня,
                                                содержащего тройные кавычки
            string_parsing_without_triple_quotes - Метод парсинга однострочного значения ключа первого уровня,
                                                   без тройных кавычек
            one_line_dictionary_parsing - Метод парсинга однострочного значения ключа первого уровня,
                                          являющегося однострочной записью словаря Python с одним уровнем вложения
            multi_line_dictionary_parsing - Метод парсинга многострочного значения ключа первого уровня,
                                            являющегося многострочным словарём Python
            vocabulary_formation - Метод формирующий вспомогательный словарь с учётом полученный строки и
                                   учётом текущего положения во вспомогательном словаре
            dots_searching - поиск и подсчёт точек перед именем ключа
            extraction_by_keyset - Метод извлечения значения для последнего ключа вспомогательного списка ключей
                                   из вспомогательного словаря
            dict_comments_extraction_by_keyset - Метод извлечение значения, для последнего ключа вспомогательного
                                                 списка ключей, из вложенного словаря комментариев вспомогательного
                                                 словаря
            recording_to_auxiliary_dictionary - Метод добавления записей во вспомогательный словарь
            single_string_parsing_without_triple_quotes - Метод парсинга одиночной строки, без тройных кавычек
            searching_a_part_of_a_string_without_a_key - Метод поиска части строки без ключа для словарей
                                                         с одним уровнем вложенности
            keys_and_values_pairs_parsing - Рекурсивный метод формирования списка пар ключей и значений для однострочной
                                            записи словаря с одним уровнем вложения
            searching_slice_of_key_and_first_found_value_in_triple_quotes - Метод поиска среза строки включающего в себя
                                                                            ключ и первое значение в тройных кавычках
            all_keys_searching - Метод поиска всех потенциальных ключей в строке.
                                 Поиск корректен в условиях отсутствия тройных кавычек в строке,
                                 где могут встречаться комбинации символов аналогичные условиям поиска данного метода.
            triple_quoted_single_string_parsing - Метод осуществляющий поиск списка или строкового значения в строке,
                                                  в которой могут быть тройные кавычки
            searching_for_a_string_slice_before_triple_quotes
            searching_comment_in_the_string - Метод поиска комментария в строке
            searching_list - Метод поиска списка в строке
            removing_the_comment_in_the_line - Метод удаления комментария из строки
            searching_string_value_without_spaces - Метод поиска строкового значения без мусорного содержимого
            triple_quotes_searching - Метод поиска тройных кавычек в строке
            framing_triple_quotes_searching - Метод поиска обрамляющих тройных кавычек для многострочного значения
            searching_of_initial_key - Метод поиска ключа в начале строки
            raw_data_dictionary_forming - Метод формирования словаря содержащего ключи первого уровня и значения
                                          этих ключей, в виде необработанных ниже находящихся строк относящихся к этим
                                          ключам. Кроме этого метод формирует вложенный словарь комментариев,
                                          содержащий заголовок и описания к файлу, комментарии к ключам первого уровня
            searching_of_file_comment_framing - Метод поиска обрамления комментариев к файлу
            primary_keys_searching - Метод поиска ключей первого уровня
            comment_string_searching - Метод поиска строки являющейся комментарием
            multiline_list_parsing - Метод парсинга многострочной записи списка для ключа верхнего уровня
            triple_hyphen_frame_searching - Метод поиска обрамляющего многострочную запись списка тройного дефиса

        Атрибуты:
            self.file (class '_io.TextIOWrapper'): дескриптор открытого .sd файла
            self.result_dict (dict): {'keys_comments': {'own_comments': ['', '', ''], }}
            self.raw_data_dict(dict): {'keys_comments': {'own_comments': ['', '', ''], }}
            self.cur_string (str): текущая строка для работы без прямой передачи строки в качестве параметра
            self.temp_string (str): вспомогательный атрибут для хранения остатка строки
            self.cur_primary_key (str): текущий ключ первого уровня
    """

    def __init__(self, file):
        """
            Метод инициализации объекта класса
            :param file: дескриптор открытого файла с данными для декодирования
        """
        self.file = file
        self.result_dict = {'keys_comments': {'own_comments': ['', '', ''], }}
        self.raw_data_dict = {'keys_comments': {'own_comments': ['', '', ''], }}
        self.cur_string = ''
        self.temp_string = ''
        self.cur_primary_key = ''

    def sd_data_decoding_management(self):
        """
            метод запускающий парсинг данных sd файла и управляющий процессом парсинга данных
        :return:
        """
        raw_data_dict = self.raw_data_dict
        self.raw_data_dictionary_forming()
        for key, strings_list in raw_data_dict.items():
            if key == 'keys_comments':
                continue
            elif key == 'unclear':
                continue
            self.cur_primary_key = key
            if not strings_list:
                key = key.strip()
                self.result_dict[key] = ''
                if key not in raw_data_dict['keys_comments']:
                    self.result_dict['keys_comments'][key] = {'own_comments': ['', '']}
                else:
                    self.result_dict['keys_comments'][key] = self.raw_data_dict['keys_comments'][key]
                continue
            initial_key = 0
            strings_list_len = len(strings_list)
            i = 0
            for elem in strings_list:
                self.cur_string = elem
                comment_string_search_res = self.comment_string_searching()
                if not comment_string_search_res:
                    triple_hyphen_frame_search_result = self.triple_hyphen_frame_searching()
                    if triple_hyphen_frame_search_result:
                        self.multiline_list_parsing()
                        break
                    framing_triple_quotes_search_res = self.framing_triple_quotes_searching()
                    if framing_triple_quotes_search_res:
                        self.multiline_string_value_parsing()
                        break
                    search_of_initial_key_res = self.searching_of_initial_key()
                    if not search_of_initial_key_res and initial_key == 0:
                        triple_quotes_search_res = self.triple_quotes_searching()
                        if triple_quotes_search_res:
                            self.string_parsing_with_triple_quotes()
                            break
                        else:
                            self.string_parsing_without_triple_quotes()
                            break
                    elif (not search_of_initial_key_res and initial_key > 0) or \
                            search_of_initial_key_res and initial_key == 0 and strings_list_len == i + 1:
                        self.one_line_dictionary_parsing()
                        break
                    elif search_of_initial_key_res and initial_key > 0:
                        self.multi_line_dictionary_parsing()
                        break
                    else:
                        initial_key += 1
                i += 1
        self.result_dict['keys_comments']['own_comments'] = self.raw_data_dict['keys_comments']['own_comments']
        self.comment_cleanup()
        return self.result_dict

    def triple_hyphen_frame_searching(self):
        """
            Метод поиска обрамляющего многострочную запись списка тройного дефиса
            :return final_result (bool): Возращает False или True
        """
        cur_sting = self.cur_string
        final_result = False
        search_pattern = r'(^ *\-\-\- *$)|(^ *\_\_\_ *$)'
        search_result = re.findall(pattern=search_pattern, string=cur_sting)
        if search_result:
            final_result = True
        else:
            pass
        return final_result

    def multiline_list_parsing(self):
        """
            Метод парсинга многострочной записи списка для ключа верхнего уровня
            :return: Ничего не возвращает. Результат парсинга сохраняется в словаре self.res_dict
        """
        raw_data_dict = self.raw_data_dict
        cur_primary_key = self.cur_primary_key
        res_dict = self.result_dict
        if cur_primary_key not in raw_data_dict['keys_comments']:
            raw_data_dict['keys_comments'][cur_primary_key] = {'own_comments': ['', '']}
        if cur_primary_key in raw_data_dict:
            framing_triple_hyphen = 0
            check = True
            multiline_dict = []
            for el in raw_data_dict[cur_primary_key]:
                pattern = r',$'
                el = re.sub(pattern, '', el)
                self.cur_string = el
                comment_sting_search_res = self.comment_string_searching()
                if check and el and comment_sting_search_res:
                    check = False
                    raw_data_dict['keys_comments'][cur_primary_key]['own_comments'][1] = el
                    continue
                elif check and el:
                    check = False
                triple_hyphen_frame_search_result = self.triple_hyphen_frame_searching()
                if triple_hyphen_frame_search_result:
                    framing_triple_hyphen += 1
                    if framing_triple_hyphen == 1:
                        continue
                    if framing_triple_hyphen == 2:
                        res_dict[cur_primary_key] = multiline_dict
                        multiline_dict = []
                        res_dict['keys_comments'][cur_primary_key] = raw_data_dict['keys_comments'][cur_primary_key]
                    continue
                if framing_triple_hyphen == 1:
                    triple_quotes_search_res = self.triple_quotes_searching()
                    if triple_quotes_search_res:
                        elem = self.triple_quoted_single_string_parsing()[1]
                    else:
                        elem = self.single_string_parsing_without_triple_quotes()
                    multiline_dict.append(elem)
                elif framing_triple_hyphen == 2:
                    multiline_dict.append(el)
            if multiline_dict and cur_primary_key in res_dict:
                res_dict['keys_comments'][cur_primary_key] = raw_data_dict['keys_comments'][cur_primary_key]
                res_dict[cur_primary_key] = 'Error while parsing the data of this key. ' \
                                            'Возможные ошибки: под закрывающими кавычками есть строки без ключей'
            elif multiline_dict:
                res_dict['keys_comments'][cur_primary_key] = raw_data_dict['keys_comments'][cur_primary_key]
                res_dict[cur_primary_key] = 'Error while paring the data of this key. ' \
                                            'Возможные ошибки: после перечисления элементов списка, отсутствует ' \
                                            'тройной знак дефиса'

    def comment_cleanup(self, comment_subdict=None, i=None):
        temp_dict = {}
        if comment_subdict:
            pattern = r'^\s*#+\s*'
            i += 1
            for key, value in comment_subdict.items():
                temp_dict[key] = None
                if key == 'own_comments':
                    temp_dict[key] = []
                    for el in value:
                        new_el = re.sub(pattern, '', el)
                        temp_dict[key].append(new_el)
                else:
                    if isinstance(value, dict):
                        sub_dict = self.comment_cleanup(value, i)
                        temp_dict[key] = sub_dict
        else:
            for key, value in self.result_dict['keys_comments'].items():
                temp_dict[key] = None
                if key == 'own_comments':
                    temp_dict[key] = []
                    k = 0
                    for el in value:
                        if k == 0:
                            pattern_1 = r'^\s*#+\s*((\\n)*|(\n)*)\s*#*\s*'
                            pattern_2 = r'((\\n)|(\n))+#+((\\n)|(\n))+$'
                            search_res = re.search(pattern_1, el)
                            if search_res:
                                new_el = el[search_res.end():]
                                if new_el:
                                    search_res = re.search(pattern_2, new_el)
                                    if search_res:
                                        new_el = new_el[:search_res.start()]
                                    temp_dict[key].append(new_el)
                                else:
                                    temp_dict[key].append('')
                        elif k == 1:
                            pattern_1 = r'#*((\\n)|(\n))+\s{0,1}#+\s{0,1}((\\n)|(\n))*#*((\\n)|(\n))*'
                            new_el = re.sub(pattern_1, '\n', el)
                            new_el = re.sub(r'^((\n)|(\\n))', '', new_el)
                            new_el = re.sub(r'((\n)|(\\n))$', '', new_el)
                            temp_dict[key].append(new_el)
                        elif k == 2:
                            pattern_1 = r'#*((\\n)|(\n))+\s{0,1}#+\s{0,1}((\\n)|(\n))*#*((\\n)|(\n))*'
                            new_el = re.sub(pattern_1, '\n', el)
                            new_el = re.sub(r'^((\n)|(\\n))', '', new_el)
                            new_el = re.sub(r'((\n)|(\\n))$', '', new_el)
                            temp_dict[key].append(new_el)
                        k += 1
                else:
                    if isinstance(value, dict):
                        i = 1
                        sub_dict = self.comment_cleanup(comment_subdict=value, i=i)
                        temp_dict[key] = sub_dict
        if comment_subdict:
            return temp_dict
        else:
            self.result_dict['keys_comments'] = temp_dict

    def multiline_string_value_parsing(self):
        """
            Метод парсинга многострочного значения для ключа первого уровня
        :return: Ничего не возвращает. Результат парсинга сохраняется в словаре self.res_dict
        """
        raw_data_dict = self.raw_data_dict
        cur_primary_key = self.cur_primary_key
        res_dict = self.result_dict
        if cur_primary_key not in raw_data_dict['keys_comments']:
            raw_data_dict['keys_comments'][cur_primary_key] = {'own_comments': ['', '']}
        if cur_primary_key in raw_data_dict:
            framing_triple_quotes = 0
            check = True
            multiline_string = ''
            for el in raw_data_dict[cur_primary_key]:
                self.cur_string = el
                comment_sting_search_res = self.comment_string_searching()
                if check and el and comment_sting_search_res:
                    check = False
                    raw_data_dict['keys_comments'][cur_primary_key]['own_comments'][1] = el
                    continue
                elif check and el:
                    check = False
                framing_triple_quotes_search_res = self.framing_triple_quotes_searching()
                if framing_triple_quotes_search_res:
                    framing_triple_quotes += 1
                    if framing_triple_quotes == 2:
                        res_dict[cur_primary_key] = multiline_string
                        multiline_string = ''
                        res_dict['keys_comments'][cur_primary_key] = raw_data_dict['keys_comments'][cur_primary_key]
                    continue
                if framing_triple_quotes == 1:
                    if not multiline_string:
                        multiline_string = el
                    else:
                        multiline_string += '\n' + el
                elif framing_triple_quotes == 2:
                    multiline_string += el
            if multiline_string:
                res_dict[cur_primary_key] = 'Error while parsing the data of this key. ' \
                                            'Возможные ошибки: под закрывающими кавычками есть строки без ключей'

    def string_parsing_with_triple_quotes(self):
        """
            Метод парсинга однострочного значения ключа первого уровня, содержащего тройные кавычки
        :return: Метод ничего не возвращает. Результат парсинга для текущего ключа сохраняется в словаре self.res_dict
        """
        raw_data_dict = self.raw_data_dict
        cur_string = self.cur_string
        cur_primary_key = self.cur_primary_key
        res_dict = self.result_dict
        if cur_primary_key not in raw_data_dict['keys_comments']:
            raw_data_dict['keys_comments'][cur_primary_key] = {'own_comments': ['', '']}
        if cur_primary_key in raw_data_dict:
            check = True
            found_value = False
            for el in raw_data_dict[cur_primary_key]:
                self.cur_string = el
                triple_quoted_single_string_pars_res = self.triple_quoted_single_string_parsing()
                if check and el:
                    comment = triple_quoted_single_string_pars_res[0]
                    check = False
                    if comment:
                        comment = comment.strip()
                        raw_data_dict['keys_comments'][cur_primary_key]['own_comments'][1] = comment
                if triple_quoted_single_string_pars_res[1] and \
                        'pars_error' not in str(triple_quoted_single_string_pars_res[1]) and not found_value:
                    res_dict[cur_primary_key] = triple_quoted_single_string_pars_res[1]
                    res_dict['keys_comments'][cur_primary_key] = raw_data_dict['keys_comments'][cur_primary_key]
                    found_value = True
                elif 'pars_error' in str(triple_quoted_single_string_pars_res[1]) and not found_value:
                    res_dict[cur_primary_key] = triple_quoted_single_string_pars_res[1]
                    found_value = True
                elif not triple_quoted_single_string_pars_res[1]:
                    res_dict[cur_primary_key] = ''
                elif found_value and triple_quoted_single_string_pars_res[1] and \
                        'pars_error' not in str(triple_quoted_single_string_pars_res[1]):
                    res_dict[cur_primary_key] = 'Error while parsing the data of this key. - ' \
                                                'под строкой со  значением есть ещё одна строка без ключа'
                elif found_value and triple_quoted_single_string_pars_res[1] and \
                        'pars_error' in str(triple_quoted_single_string_pars_res[1]):
                    res_dict[cur_primary_key] = 'Error while parsing the data of this key. - ' \
                                                'под строкой со  значением есть ещё одна строка без ключа, ' \
                                                'в которой содержатся ошибки: ' + \
                                                str(triple_quoted_single_string_pars_res[1])

    def string_parsing_without_triple_quotes(self):
        """
            Метод парсинга однострочного значения ключа первого уровня, без тройных кавычек
        :return:
        """
        raw_data_dict = self.raw_data_dict
        cur_string = self.cur_string
        cur_primary_key = self.cur_primary_key
        res_dict = self.result_dict
        if cur_primary_key not in raw_data_dict['keys_comments']:
            raw_data_dict['keys_comments'][cur_primary_key] = {'own_comments': ['', '']}
        if cur_primary_key in raw_data_dict:
            check = True
            found_value = False
            for el in raw_data_dict[cur_primary_key]:
                self.cur_string = el
                comment = self.searching_comment_in_the_string().strip()
                if check and el and comment:
                    check = False
                    raw_data_dict['keys_comments'][cur_primary_key]['own_comments'][1] = comment
                elif check and el:
                    check = False
                searching_list_result = self.searching_list()
                if searching_list_result and searching_list_result != 'list_read_error' and not found_value:
                    res_dict[cur_primary_key] = searching_list_result
                    found_value = True
                elif searching_list_result == 'list_read_error' and not found_value:
                    res_dict[cur_primary_key] = 'Error while parsing the data of this key. ' \
                                                'Возможные ошибки: в строке со списком пропущена запятая,' \
                                                'возможно имеется пробел в значении одного из элементов списка,' \
                                                'возможно имеется мусорное содержимое, отделённое пробелом от ' \
                                                'последнего элемента списка'
                    found_value = True
                elif not found_value and not searching_list_result:
                    searching_string_value_result = self.searching_string_value_without_spaces()
                    if searching_string_value_result:
                        res_dict[cur_primary_key] = searching_string_value_result
                    a = self.cur_string
                    if self.cur_string:
                        res_dict[cur_primary_key] = 'Error while parsing the data of this key. ' \
                                                    'Возможные ошибки: строка имеющая пробел в значении не имеет ' \
                                                    'тройных кавычек или же в значении присутствует ' \
                                                    'случайно поставленный пробел'
                    self.temp_string = ''
                    found_value = True
                elif found_value and not searching_list_result:
                    searching_string_value_result = self.searching_string_value_without_spaces()
                    if searching_string_value_result:
                        res_dict[cur_primary_key] = 'Error while parsing the data of this key. ' \
                                                    'Возможные ошибки: в строке под ключом находится ещё одна строка'
                    if self.cur_string:
                        res_dict[cur_primary_key] = 'Error while parsing the data of this key. ' \
                                                    'Возможные ошибки: в строке под ключом находится ещё одна строка,' \
                                                    ' которая к тому же имеет пробел в значении и не имеет ' \
                                                    'тройных кавычек или же в её значении присутствует ' \
                                                    'случайно поставленный пробел'
                    self.temp_string = ''
                elif found_value and searching_list_result and searching_list_result != 'list_read_error':
                    res_dict[cur_primary_key] = 'Error while parsing the data of this key. ' \
                                                'Возможные ошибки: в строке под ключом находится ещё одна строка' \
                                                ' со списком'
                elif found_value and searching_list_result == 'list_read_error':
                    res_dict[cur_primary_key] = 'Error while parsing the data of this key. ' \
                                                'Возможные ошибки: в строке под ключом находится ещё одна строка' \
                                                'в этой строке со списком пропущена запятая,' \
                                                'возможно имеется пробел в значении одного из элементов списка,' \
                                                'возможно имеется мусорное содержимое, отделённое пробелом от ' \
                                                'последнего элемента списка'
            res_dict['keys_comments'][cur_primary_key] = raw_data_dict['keys_comments'][cur_primary_key]

    def one_line_dictionary_parsing(self):
        """
            Метод парсинга однострочного значения ключа первого уровня, являющегося однострочной записью словаря
            с одним уровнем вложения
        :return:
        """
        raw_data_dict = self.raw_data_dict
        cur_string = self.cur_string
        cur_primary_key = self.cur_primary_key
        res_dict = self.result_dict
        work_dict = {}
        if cur_primary_key not in raw_data_dict['keys_comments']:
            raw_data_dict['keys_comments'][cur_primary_key] = {'own_comments': ['', '']}
        if cur_primary_key in raw_data_dict:
            check = True
            found_value = False
            stop_work = False
            keys_and_value_processed_list = []
            for el in raw_data_dict[cur_primary_key]:
                self.cur_string = el
                keys_and_values_pairs_list = self.keys_and_values_pairs_parsing()
                if keys_and_values_pairs_list and isinstance(keys_and_values_pairs_list, list):
                    for e in keys_and_values_pairs_list:
                        key = self.searching_of_initial_key(cur_str=e)
                        part_of_a_string_without_a_key = self.searching_a_part_of_a_string_without_a_key(cur_str=e,
                                                                                                         key=key)
                        triple_quotes_search_res = self.triple_quotes_searching(part_of_a_string_without_a_key)
                        key = key.strip()
                        key = key.lstrip('.')
                        w_str = ''
                        comment = ''
                        self.cur_string = part_of_a_string_without_a_key
                        if triple_quotes_search_res:
                            str_pars_res = self.triple_quoted_single_string_parsing()
                            if str_pars_res:
                                w_str = str_pars_res[1]
                                comment = str_pars_res[0]
                        else:
                            w_str = self.searching_list(part_of_a_string_without_a_key)
                            if not isinstance(w_str, list) or w_str == []:
                                str_pars_res = ['', '']
                                comment = self.searching_comment_in_the_string()
                                w_str = self.single_string_parsing_without_triple_quotes()
                                if w_str == []:
                                    w_str = ''
                                if self.cur_string:
                                    w_str = 'Error_parsing: Ошибка. Возможно отсутствуют тройные кавычки для значения' \
                                            'содержащего пробелы, возможно отсутствует запятая для списка'
                            else:
                                str_pars_res = ['', w_str]
                        keys_and_value_processed_list.append([key, w_str, comment])
                        if str_pars_res[1] and isinstance(str_pars_res[1], list) and not stop_work:
                            self.multi_line_dictionary_parsing()
                            stop_work = True
                    if stop_work:
                        break
                    str_for_comment_search = ''
                    len_kv_list = len(keys_and_values_pairs_list)
                    n = 0
                    for e in keys_and_value_processed_list:
                        key = e[0]
                        value = e[1]
                        comment = e[2]
                        if len_kv_list == n + 1:
                            check = True
                        else:
                            check = False
                        if key:
                            if comment and len_kv_list == n + 1:
                                raw_data_dict['keys_comments'][cur_primary_key]['own_comments'][1] = comment
                            work_dict[key] = value
                        else:
                            key = key.strip()
                            key = key.lstrip('.')
                            work_dict[key] = ''
                        n += 1
                elif keys_and_values_pairs_list:
                    work_dict = keys_and_values_pairs_list
                res_dict[cur_primary_key] = work_dict
                res_dict['keys_comments'][cur_primary_key] = raw_data_dict['keys_comments'][cur_primary_key]

    def multi_line_dictionary_parsing(self):
        """
            Метод парсинга многострочного значения ключа первого уровня, являющегося многострочным словарём

            Используемые переменные:
                raw_data_dict (dict):  словарь содержащий списки необработанных строк для ключей первого уровня
                cur_string (str):  текущая строка находящаяся в работе
                cur_primary_key (str): текущий ключ верхнего уровня
                res_dict (dict):
                work_dict (dict):
                auxiliary_dict (dict): вспомогательный словарь
                auxiliary_list (list): вспомогательный список необходимый для отслеживания текущего положения в словаре
            :return:
        """
        raw_data_dict = self.raw_data_dict
        cur_string = self.cur_string
        cur_primary_key = self.cur_primary_key
        res_dict = self.result_dict
        work_dict = {}
        auxiliary_dict = {'root': {}, 'keys_comments': {}}
        auxiliary_list = ['root']
        if cur_primary_key not in raw_data_dict['keys_comments']:
            raw_data_dict['keys_comments'][cur_primary_key] = {'own_comments': ['', '']}
        if cur_primary_key in raw_data_dict:
            check = True
            found_value = False
            for el in raw_data_dict[cur_primary_key]:
                self.cur_string = el
                if check and el:
                    comment_str_search_res = self.comment_string_searching()
                    if comment_str_search_res:
                        comment = self.cur_string.strip()
                        check = False
                        if comment:
                            raw_data_dict['keys_comments'][cur_primary_key]['own_comments'][1] = comment
                        continue
                initial_key = self.searching_of_initial_key()
                if initial_key:
                    vocabulary_formation_res = self.vocabulary_formation(cur_key=initial_key,
                                                                         auxiliary_list=auxiliary_list,
                                                                         auxiliary_dict=auxiliary_dict)
                    auxiliary_list = vocabulary_formation_res[0]
                    auxiliary_dict = vocabulary_formation_res[1]
                else:
                    pass
            f_dict = {}
            f_dict = self.final_dictionary_forming(auxiliary_dict, f_dict)
            res_dict[cur_primary_key] = f_dict['root']
            res_dict['keys_comments'][cur_primary_key] = f_dict['keys_comments']
            res_dict['keys_comments'][cur_primary_key]['own_comments'] = \
                raw_data_dict['keys_comments'][cur_primary_key]['own_comments']
            del auxiliary_dict

    def vocabulary_formation(self, cur_key, auxiliary_list, auxiliary_dict):
        """
            Метод формирующий вспомогательный словарь с учётом полученный строки и учётом текущего положения
             во вспомогательном словаре
            :param cur_key: текущий ключ первого уровня
            :param auxiliary_list: вспомогательный список ключей, необходимый для фиксации текущего положения в словаре
            :param auxiliary_dict: вспомогательный словарь
            Используемые переменные:
                n_dots - число точек перед именем ключа
                len_auxiliary_list - размер вспомогательного списка ключей
                temp_auxiliary_list - временный список для переформирования основного вспомогательного списка
            Используемые методы:
                self.dots_searching() - метод определения числа точек перед именем ключа
                self.recording_to_auxiliary_dictionary -
            :return: [auxiliary_list, auxiliary_dict]
        """
        cur_string = self.cur_string.rstrip()
        n_dots = self.dots_searching(cur_key)
        len_auxiliary_list = len(auxiliary_list)
        if len_auxiliary_list - 1 == n_dots:
            auxiliary_list[n_dots] = cur_key
            auxiliary_dict = self.recording_to_auxiliary_dictionary(auxiliary_list, auxiliary_dict, cur_key)
        elif len_auxiliary_list > n_dots:
            i = 0
            temp_auxiliary_list = []
            for el in auxiliary_list:
                if i < n_dots:
                    temp_auxiliary_list.append(el)
                elif i == n_dots:
                    temp_auxiliary_list.append(cur_key)
                    auxiliary_list = temp_auxiliary_list
                    break
                i += 1
            auxiliary_dict = self.recording_to_auxiliary_dictionary(auxiliary_list, auxiliary_dict, cur_key)
        elif n_dots == len_auxiliary_list:
            auxiliary_list.append(cur_key)
            auxiliary_dict = self.recording_to_auxiliary_dictionary(auxiliary_list, auxiliary_dict, cur_key)
        return [auxiliary_list, auxiliary_dict]

    def dots_searching(self, cur_key):
        """
            Метод поиска и подсчёта точек перед именем ключа
            :param cur_key: ключ для которого необходимо осуществить подсчёт точек
            :return: number_dots (int)
        """
        cur_string = self.cur_string
        number_dots = int
        search_pattern = r'\.'
        search_result = re.findall(pattern=search_pattern, string=cur_key)
        if search_result:
            number_dots = len(search_result)
        else:
            if cur_string:
                number_dots = 1
            else:
                number_dots = False
        return number_dots

    def extraction_by_keyset(self, a_list, a_dict, cur_index=0):
        """
        Рекурсивный метод извлечения значения для последнего ключа вспомогательного списка ключей
        из вспомогательного словаря
        :param a_list: текущий вспомогательный список
        :param a_dict: текущий вспомогательный словарь
        :param cur_index: текущая позиция во вспомогательном словаре
        :return: s_by_key: извлечённое значение из вспомогательного словаря
        """
        len_a_list = len(a_list)
        key_name = a_list[cur_index]
        if key_name in a_dict:
            s_by_key = a_dict[key_name]
            if len_a_list - 2 > cur_index:
                cur_index += 1
                s_by_key = self.extraction_by_keyset(a_list, s_by_key, cur_index)
            else:
                pass
        else:
            return a_dict
        return s_by_key

    def dict_comments_extraction_by_keyset(self, a_list, a_dict, cur_index=0):
        """
            Метод извлечение значения, для последнего ключа вспомогательного списка ключей, из вложенного словаря
            комментариев вспомогательного словаря
            :param a_list:
            :param a_dict:
            :param cur_index:
            :return:
            """
        len_a_list = len(a_list)
        if cur_index == 0:
            key_name = 'keys_comments'
        else:
            key_name = a_list[cur_index]
        if key_name in a_dict:
            s_by_key = a_dict[key_name]
            if len_a_list - 2 > cur_index:
                cur_index += 1
                s_by_key = self.dict_comments_extraction_by_keyset(a_list, s_by_key, cur_index)
            else:
                pass
        else:
            return a_dict
        return s_by_key

    def final_dictionary_forming(self, t_dict, r_dict):
        """
        Метод очистки ключей от точек перед их именами
        :param t_dict:
        :param r_dict:
        :return:
        """
        wt_dict = {}
        wr_dict = {}
        for key, value in t_dict.items():
            if isinstance(value, dict):
                if value == {}:
                    key = key.replace('.', '')
                    wr_dict[key] = ''
                    continue
                wt_dict = value
                subdict = self.final_dictionary_forming(wt_dict, wr_dict)
                key = key.replace('.', '')
                wr_dict[key] = subdict
            else:
                key = key.replace('.', '')
                wr_dict[key] = value
        return wr_dict

    def recording_to_auxiliary_dictionary(self, auxiliary_list, auxiliary_dict, cur_key):
        """
            Метод добавления записей во вспомогательный словарь
            :param auxiliary_list: вспомогательный список ключей, необходимый для фиксации текущего положения в словаре
            :param auxiliary_dict: вспомогательный словарь
            :param cur_key: текущий ключ первого уровня
            Используемые методы:
                self.extraction_by_keyset() - извлечение значения словаря для последнего ключа из вспомогательн. списка
                self.dict_comments_extraction_by_keyset() - извлечение знач. словаря комментариев для посл. кл. всп. сп.
                self.triple_quotes_searching() - поиск обрамляющих тройных кавычек
                self.searching_a_part_of_a_string_without_a_key() - поиска части строки без ключа
                self.triple_quoted_single_string_parsing() - поиск значения в строке, содержащей тройные кавычки
                self.searching_list() - поиск списка в строке без ключа
                self.searching_string_value_without_spaces() - поиск значения, как части строки без пробелов
            Используемые переменные:

            :return: auxiliary_dict (dict) итоговый вспомогательный словарь
        """
        selected_by_key = self.extraction_by_keyset(auxiliary_list, auxiliary_dict)
        selected_by_key_for_comments = self.dict_comments_extraction_by_keyset(auxiliary_list, auxiliary_dict)
        triple_quotes_searching_res = self.triple_quotes_searching()
        if cur_key not in selected_by_key_for_comments:
            selected_by_key_for_comments[cur_key] = {}
        selected_by_key_for_comments[cur_key]['own_comments'] = []
        selected_by_key_for_comments[cur_key]['own_comments'].append('')
        if triple_quotes_searching_res:
            self.cur_string = self.searching_a_part_of_a_string_without_a_key(cur_str=self.cur_string,
                                                                              key=cur_key)
            found_value = self.triple_quoted_single_string_parsing()
            if found_value:
                selected_by_key[cur_key] = found_value[1]
                selected_by_key_for_comments[cur_key]['own_comments'].append(found_value[0])
            else:
                # selected_by_key[cur_key] = {}
                selected_by_key_for_comments[cur_key]['own_comments'].append('')
        else:
            self.cur_string = self.searching_a_part_of_a_string_without_a_key(cur_str=self.cur_string,
                                                                              key=cur_key)
            if self.cur_string:
                str_for_comments_search = self.cur_string
                searching_list_res = self.searching_list()
                if searching_list_res and isinstance(searching_list_res, list):
                    selected_by_key[cur_key] = searching_list_res
                    comment = self.searching_comment_in_the_string(str_for_comments_search)
                    if comment:
                        selected_by_key_for_comments[cur_key]['own_comments'].append(comment)
                    else:
                        selected_by_key_for_comments[cur_key]['own_comments'].append('')
                else:
                    searching_string_value_without_spaces_res = self.searching_string_value_without_spaces()
                    if searching_string_value_without_spaces_res and not self.cur_string:
                        selected_by_key[cur_key] = searching_string_value_without_spaces_res
                    elif searching_string_value_without_spaces_res:
                        selected_by_key[cur_key] = 'Error while parsing the data of this key. ' \
                                                   'Возможные ошибки: в строке со списком пропущена запятая,' \
                                                   'возможно имеется пробел в значении одного из элементов списка,' \
                                                   'возможно имеется мусорное содержимое, отделённое пробелом от ' \
                                                   'последнего элемента списка'
                    else:
                        selected_by_key[cur_key] = {}
                    comment = self.searching_comment_in_the_string(str_for_comments_search)
                    if comment:
                        selected_by_key_for_comments[cur_key]['own_comments'].append(comment)
                    else:
                        selected_by_key_for_comments[cur_key]['own_comments'].append('')
            else:
                selected_by_key[cur_key] = {}
                selected_by_key_for_comments[cur_key]['own_comments'].append('')
        return auxiliary_dict

    def single_string_parsing_without_triple_quotes(self):
        """
            Метод парсинга одиночной строки, без тройных кавычек
        :return:
        """
        res_list = []
        res_str = ''
        final_res = None
        searching_list_result = self.searching_list()
        if searching_list_result and searching_list_result != 'list_read_error':
            res_list = searching_list_result
        elif searching_list_result == 'list_read_error':
            res_str = 'Error while parsing the data of this key. ' \
                      'Возможные ошибки: в строке со списком пропущена запятая,' \
                      'возможно имеется пробел в значении одного из элементов списка,' \
                      'возможно имеется мусорное содержимое, отделённое пробелом от ' \
                      'последнего элемента списка'
        else:
            search_str_res = self.searching_string_value_without_spaces()
            if not self.cur_string:
                res_str = search_str_res
            else:
                res_str = 'Error while parsing the data of this key. ' \
                          'Возможные ошибки: в строке c пробелами отсутствуют тройные кавычки' \
                          'возможно имеется случайный пробел, возможно нет знака # перед комментарием'
        if res_str:
            final_res = res_str
        else:
            final_res = res_list
        return final_res

    def searching_a_part_of_a_string_without_a_key(self, cur_str=None, key=None):
        """
            Метод поиска части строки без ключа для словарей с одним уровнем вложенности
        :return:
        """
        if not cur_str:
            cur_string = self.cur_string
        else:
            cur_string = cur_str
        if not key:
            key = ''
        else:
            key = str(key)
        final_result = ''
        search_pattern = r'(?<=' + key + r')\s*:\s*'
        search_result = re.search(pattern=search_pattern, string=cur_string)
        if search_result:
            final_result = cur_string[search_result.end():]
            final_result = re.sub(r',$', '', final_result)
            final_result = re.sub(r'^,', '', final_result)
        return final_result

    def keys_and_values_pairs_parsing(self, cur_str=None, part_pair=None, n=None):
        """
            Рекурсивный метод формирования списка пар ключей и значений для однострочной записи словаря с одним уровнем вложения
            :param cur_str: - явно переданная строка в которой будет вестись поиск пар ключей и их значений
            :param part_pair: часть строки содержащая ключ и часть строки до первого значения в тройных кавычках
            :param n: текущая глубина рекурсии
            Некоторые используемые переменные:
                cur_string (str): строка в которой ведётся поиск пар
                all_keys_search_res: итератор с объектами Match для найденных потенциальных ключах в строке
                start_el: последний перебранный элемент  all_keys_search_res, используемый для определения начала среза
                          пары ключа и значения
                start - точка начала среза
                end - точка окончания среза
                pair - часть строки содержащая пару ключа и его значения
                str_slice - результат поиска части строки содержащей ключ и часть строки до значения в тройных кавычках
                part_pair - срез строки содержащий ключ и часть строки до значения в тройных кавычках
                work_part_string - вспомогательная переменная для хранения части строки

            Используемые методы:
                all_keys_searching() - поиск всех потенциальных ключей в строке
                triple_quotes_searching() - поиск тройных кавычек
                searching_slice_of_key_and_first_found_value_in_triple_quotes() - поиск ключа и первого значения
                                                                                  в тройных кавычках
            :return: keys_and_values_pairs_list (list) - список пар ключей и их значений
        """
        if not n:
            n = 1
        else:
            n += 1
        if n == 900:
            return 'pars_error - Возможно слишком большая строка, в которой слишком много значений в тройных кавычках'
        if not cur_str:
            cur_string = self.cur_string
        else:
            cur_string = cur_str
        keys_and_values_pairs_list = []
        all_keys_search_res = self.all_keys_searching(cur_str=cur_string)
        start_el = None
        if all_keys_search_res:
            for el in all_keys_search_res:
                if start_el:
                    start = start_el.start()
                    end = el.start()
                    pair = cur_string[start: end]
                    triple_quotes_search_res = self.triple_quotes_searching(cur_str=pair)
                    if not triple_quotes_search_res:
                        keys_and_values_pairs_list.append(pair)
                    else:
                        work_part_string = cur_string[start:]
                        str_slice = self.searching_slice_of_key_and_first_found_value_in_triple_quotes(work_part_string)
                        if str_slice:
                            part_pair = work_part_string[str_slice.start(): str_slice.end()]
                            work_part_string = work_part_string[str_slice.end():]
                            part_of_kv_pairs_list = self.keys_and_values_pairs_parsing(cur_str=work_part_string,
                                                                                       part_pair=part_pair, n=n)
                            if part_of_kv_pairs_list and isinstance(part_of_kv_pairs_list, list):
                                keys_and_values_pairs_list.extend(part_of_kv_pairs_list)
                                return keys_and_values_pairs_list
                            else:
                                return part_of_kv_pairs_list
                        else:
                            return 'pars_error - Ошибка разбора строки. Возможно не хватает закрывающих' \
                                   'возможно есть случайный пробел или значение содержащее пробелы не содержит' \
                                   ' обрамляющих кавычек'
                    start_el = el
                else:
                    if part_pair:
                        work_part_string = cur_string[:el.start()]
                        triple_quotes_search_res = self.triple_quotes_searching(cur_str=work_part_string)
                        if not triple_quotes_search_res:
                            pair = part_pair + cur_string[:el.start()]
                            keys_and_values_pairs_list.append(pair)
                        else:
                            work_part_string = cur_string
                            str_slice = self.searching_slice_of_key_and_first_found_value_in_triple_quotes(
                                work_part_string)
                            if str_slice:
                                part_pair = part_pair + work_part_string[str_slice.start(): str_slice.end()]
                                work_part_string = work_part_string[str_slice.end():]
                                part_of_kv_pairs_list = self.keys_and_values_pairs_parsing(cur_str=work_part_string,
                                                                                           part_pair=part_pair, n=n)
                                if part_of_kv_pairs_list and isinstance(part_of_kv_pairs_list, list):
                                    keys_and_values_pairs_list.extend(part_of_kv_pairs_list)
                                    return keys_and_values_pairs_list
                                else:
                                    return part_of_kv_pairs_list
                            else:
                                return 'pars_error - Ошибка разбора строки. Возможно не хватает обрамляющих кавычек' \
                                       'возможно есть случайный пробел или значение содержащее пробелы не содержит' \
                                       ' обрамляющих кавычек'
                    start_el = el
                    continue
            if start_el:
                start = start_el.start()
                end = None
                pair = cur_string[start: end]
                keys_and_values_pairs_list.append(pair)
        else:
            if part_pair:
                pair = part_pair + cur_string
            else:
                pair = cur_string
            keys_and_values_pairs_list.append(pair)
        return keys_and_values_pairs_list

    def searching_slice_of_key_and_first_found_value_in_triple_quotes(self, cur_str=None):
        """
            Метод поиска среза строки включающего в себя ключ и первое значение в тройных кавычках
        :return:
        """
        if not cur_str:
            cur_string = self.cur_string
        else:
            cur_string = cur_str
        search_pattern = r"(.*?((''')|(\"\"\")|(\\'\\'\\')|(\\\"\\\"\\\")).*?((''')|(\"\"\")|(\\'\\'\\')|" \
                         r"(\\\"\\\"\\\")))"
        search_result = re.search(pattern=search_pattern, string=cur_string)
        return search_result

    def all_keys_searching(self, cur_str=None):
        """
            Метод поиска всех потенциальных ключей в строке. Поиск корректен в условиях отсутствия тройных кавычек
            в строке, где могут встречаться комбинации аналогичные условиям поиска данного метода.
        :return:
        """
        if not cur_str:
            cur_string = self.cur_string
        else:
            cur_string = cur_str
        search_pattern = r'(^ *\.*([A-Za-z][A-Za-z0-9_]+)\s*(?=:))|((?<=,) *\.*([A-Za-z][A-Za-z0-9_]+)\s*(?=:))'
        search_result = re.finditer(pattern=search_pattern, string=cur_string)
        return search_result

    def triple_quoted_single_string_parsing(self):
        """
            Метод осуществляющий поиск списка или строкового значения в строке, в которой есть тройные кавычки
            Переменные и атрибуты:
                found_list (list): Итоговый найденный список
                found_str (str): Найденная строка
                found_comment (str): Найденный комментарий в строке
                undefined_value: Не распределённая часть строки
                self.cur_string (str): Строка находящаяся в работе
                part_inside_triple_quotes (str): Часть строки находящаяся внутри тройных кавычек
                triple_quotes (int): число найденных тройных кавычек
            Используемые методы:
                self.triple_quotes_searching() - поиск тройных кавычек
                self.searching_for_a_string_slice_before_triple_quotes() - поиск части строки до тройных кавычек
                self.searching_list() - поиск списка
                self.searching_comment_in_the_string() - поиск комментария в строке
                self.removing_the_comment_in_the_line() - удаление комментария из строки
        :return:
            string_parsing_result (list): Возвращает сформированный список [found_comment, found_list|found_str]

        """
        found_list = []
        found_str = ''
        found_comment = ''
        undefined_value = None
        string_parsing_result = []
        cur_string = self.cur_string
        part_inside_triple_quotes = None
        triple_quotes = 0
        i = 0
        while self.cur_string:
            triple_quotes_search_res = self.triple_quotes_searching()
            if triple_quotes_search_res:
                triple_quotes += 1
                string_slice = self.searching_for_a_string_slice_before_triple_quotes()
                if "'''" in string_slice or '"""' in string_slice:
                    string_slice = string_slice[: -3]
                elif "\\'\\'\\'" in string_slice or '\\"\\"\\"' in string_slice:
                    string_slice = string_slice[: -6]
                if not part_inside_triple_quotes and triple_quotes != 1:
                    part_inside_triple_quotes = True
                else:
                    part_inside_triple_quotes = False
                if string_slice:
                    if not part_inside_triple_quotes:
                        list_part = self.searching_list(cur_str=string_slice)
                        if list_part and list_part != 'list_read_error':
                            if list_part[0] == '':
                                list_part.pop(0)
                            if undefined_value:
                                found_list.append(undefined_value)
                                undefined_value = None
                            found_list.extend(list_part)
                        elif list_part == 'list_read_error':
                            if not string_parsing_result:
                                string_parsing_result.append('')
                            string_parsing_result.append('pars_error - Ошибка формирования списка. '
                                                         'Возможно есть пропущенные запятые, '
                                                         'возможно есть случайный пробел или значение содержащее'
                                                         ' пробелы не содержит обрамляющих кавычек')
                            return string_parsing_result
                        else:
                            if not string_parsing_result:
                                string_parsing_result.append('')
                            string_parsing_result.append('pars_error - есть символы не попавшие в тройные кавычки или'
                                                         ' отсутствует запятая')
                            return string_parsing_result
                    else:
                        if not undefined_value and found_list:
                            found_list.append(string_slice)
                        elif not undefined_value:
                            undefined_value = string_slice
                        else:
                            if not string_parsing_result:
                                string_parsing_result.append('')
                            string_parsing_result.append('pars_error - есть символы не попавшие в тройные кавычки или'
                                                         ' отсутствует запятая')
                            return string_parsing_result
                else:
                    if not self.cur_string:
                        if part_inside_triple_quotes:
                            if found_list:
                                found_list.append('')
                        else:
                            if not string_parsing_result:
                                string_parsing_result.append('')
                            string_parsing_result.append('pars_error - проблема с тройными кавычками в строке')
                            return string_parsing_result
                    else:
                        continue
            else:
                found_comment = self.searching_comment_in_the_string()
                if not string_parsing_result:
                    string_parsing_result.append(found_comment)
                else:
                    string_parsing_result[0] = found_comment
                self.removing_the_comment_in_the_line()
                division_remainder = triple_quotes % 2
                if division_remainder != 0:
                    string_parsing_result.append('pars_error - проблема с тройными кавычками в строке')
                    return string_parsing_result
                if not self.cur_string and undefined_value:
                    found_str = undefined_value
                    undefined_value = None
                    continue
                elif not self.cur_string:
                    continue
                elif found_list:
                    list_part = self.searching_list()
                    if list_part and list_part != 'list_read_error':
                        if undefined_value:
                            found_list.append(undefined_value)
                            undefined_value = None
                        if list_part[0] == '':
                            list_part.pop(0)
                        found_list.extend(list_part)
                        self.cur_string = ''
                    elif list_part and list_part == 'list_read_error':
                        string_parsing_result.append(
                            'pars_error - Ошибка формирования списка. Возможно есть пропущенные запятые, '
                            'возможно есть случайный пробел или значение содержащее пробелы не содержит'
                            ' обрамляющих кавычек')
                        return string_parsing_result
                    else:
                        string_parsing_result.append(
                            'pars_error - Есть лишние символы за пределами обрамляющих тройных кавычек или '
                            'пропущена запятая')
                        return string_parsing_result
                elif not found_list and undefined_value:
                    self.cur_string = self.cur_string.strip()
                    list_part = self.searching_list()
                    if list_part and list_part != 'list_read_error' or not list_part and ',' in self.cur_string:
                        if list_part and list_part[0] == '':
                            list_part.pop(0)
                        found_list.append(undefined_value)
                        undefined_value = None
                        found_list.extend(list_part)
                        self.cur_string = ''
                    elif list_part and list_part == 'list_read_error':
                        string_parsing_result.append(
                            'pars_error - Ошибка формирования списка. Возможно есть пропущенные запятые, '
                            'возможно есть случайный пробел или значение содержащее пробелы не содержит'
                            ' обрамляющих кавычек')
                        return string_parsing_result
                    elif not list_part and self.cur_string:
                        string_parsing_result.append(
                            'pars_error - Есть лишние символы за пределами обрамляющих тройных кавычек или '
                            'пропущена запятая')
                        return string_parsing_result
                elif not found_list and not undefined_value and ',' in self.cur_string:
                    string_parsing_result.append(['', ])
                    return string_parsing_result
                else:
                    string_parsing_result.append('pars_error')
                    return string_parsing_result
                i += 1
                if i == 1000:
                    if not string_parsing_result:
                        string_parsing_result.append('')
                    string_parsing_result.append('pars_error - Слишком много циклов. Возможно это вызвано багом '
                                                 'библиотеки или '
                                                 'слишком длинным значением для текущего ключа')
                    return string_parsing_result

        if found_list:
            if not string_parsing_result:
                string_parsing_result.append('')
            string_parsing_result.append(found_list)
        elif found_str:
            if not string_parsing_result:
                string_parsing_result.append('')
            string_parsing_result.append(found_str)
        elif undefined_value:
            found_str = undefined_value
            if not string_parsing_result:
                string_parsing_result.append('')
            string_parsing_result.append(found_str)
        else:
            if not string_parsing_result:
                string_parsing_result.append('')
            string_parsing_result.append('')
        return string_parsing_result

    def searching_for_a_string_slice_before_triple_quotes(self):
        cur_sting = self.cur_string
        if not cur_sting:
            return ''
        final_result = ''
        search_pattern = r'.*?(\"\"\"|\'\'\'|\\\"\\\"\\\"|\\\'\\\'\\\')'
        search_result = re.search(pattern=search_pattern, string=cur_sting)
        if search_result:
            end = search_result.end()
            start = search_result.start()
            final_result = cur_sting[start: end]
            self.cur_string = self.cur_string[end:]
        return final_result

    def searching_comment_in_the_string(self, cur_str=None):
        """
            Метод поиска комментария в строке
        :return:
            comment (str): возвращает найденный в строке комментарий
        """
        if not cur_str:
            cur_string = self.cur_string
        else:
            cur_string = cur_str
        comment = ''
        pattern = r'(\s*\#[^#]+)$'
        search_result = re.search(pattern=pattern, string=cur_string)
        if search_result:
            comment = cur_string[search_result.start(): search_result.end()]
        comment = comment.strip()
        return comment

    def searching_list(self, cur_str=None):
        """
            Метод поиска списка в строке
            :param cur_str: строка в которой необходимо искать список. Если параметр не передан, то по умолчанию поиск
                            будет вестись в атрибуте класса self.cur_string
            Используемые методы:
                removing_the_comment_in_the_line() - удаление комментариев из строки
                (комментарий удаляется только при работе с атрибутом self.cur_string)
                self.searching_string_value_without_spaces() - поиск от начала строки её части без пробелов
            Используемые переменные и атрибуты:
                self.temp_string (str): часть строки оставшаяся после поиска части строки без пробелов,
                                        используемая при работе без атрибута self.cur_string
            :return final_result (list): возвращаем найденный список
        """
        if cur_str:
            cur_string = cur_str
        else:
            self.removing_the_comment_in_the_line()
            cur_string = self.cur_string.rstrip()
        cur_string = cur_string.replace(',', ' ,')
        cur_string = cur_string.rstrip()
        final_result = []
        search_some_keys_pattern = r'^[^,]+(?=,)|(?<=,)[^,]+'  # ищем элементы списка
        search_some_keys_result = re.findall(pattern=search_some_keys_pattern, string=cur_string)
        if search_some_keys_result:
            for el in search_some_keys_result:
                el = el.strip()
                if el != '':
                    el_value_search_res = self.searching_string_value_without_spaces(el)
                    if not self.temp_string:
                        el_value = el_value_search_res
                        final_result.append(el_value)
                    else:
                        final_result = 'list_read_error'
                        self.temp_string = ''
                        return final_result
                else:
                    final_result.append(el)
        return final_result

    def removing_the_comment_in_the_line(self, cur_str=None):
        """
            Метод удаления комментария из строки
            :param cur_str: Переданная строка для очистки от комментария
            :return: Результат только в случае работы с переданной строкой
                cur_string (str): Строка очищенная от комментария
                Если строка не передавалась при вызове, то результат сохраняется в атрибуте self.cur_string
        """
        if not cur_str:
            cur_string = self.cur_string
        else:
            cur_string = cur_str
        search_pattern = r'(\s*\#[^#]+)$'
        search_result = re.search(pattern=search_pattern, string=cur_string)
        if search_result and not cur_str:
            self.cur_string = cur_string[: search_result.start()]
        elif search_result and cur_str:
            cur_string = cur_string[: search_result.start()]
            return cur_string

    def searching_string_value_without_spaces(self, cur_str=None):
        """
            Метод поиска строкового значения без мусорного содержимого
            Используемые методы:
                removing_the_comment_in_the_line() - удаление комментария из строки
                (Комментарий удаляется из строки только при работе с атрибутом self.cur_string)
            :return: final_result (str): Строка до пробелов. Остаток строки сохраняется в self.cur_string.
                Если строка не передавалась при вызове, то остаток строки сохраняется в атрибуте self.temp_string
        """
        if cur_str:
            cur_string = cur_str
        else:
            self.removing_the_comment_in_the_line()
            cur_string = self.cur_string.rstrip()
        final_result = ''
        search_pattern = r'\S+'
        search_result = re.search(pattern=search_pattern, string=cur_string)
        if search_result:
            final_result = cur_string[search_result.start(): search_result.end()]
            if cur_str:
                self.temp_string = cur_string[search_result.end():]
            else:
                self.cur_string = cur_string[search_result.end():]
        return final_result

    def triple_quotes_searching(self, cur_str=None):
        """
            Метод поиска тройных кавычек в строке
        :return final_result (bool): True or False
        """
        if not cur_str:
            cur_string = self.cur_string
        else:
            cur_string = cur_str
        final_result = False
        search_pattern = r'(\"\"\"|\'\'\'|\\\"\\\"\\\"|\\\'\\\'\\\')'
        search_result = re.search(pattern=search_pattern, string=cur_string)
        if search_result:
            final_result = True
        return final_result

    def framing_triple_quotes_searching(self):
        """
            Метод поиска обрамляющих тройных кавычек записанного многострочного значения
        :return final_result (bool): Возращает False или True
        """
        cur_sting = self.cur_string
        final_result = False
        search_pattern = r'(^ *\"\"\" *$)|(^ *\'\'\' *$)|(^ *\\\"\\\"\\\" *$)|(^ *\\\'\\\'\\\' *$)'
        search_result = re.findall(pattern=search_pattern, string=cur_sting)
        if search_result:
            final_result = True
        else:
            pass
        return final_result

    def searching_of_initial_key(self, cur_str=None):
        """
            Метод поиска ключа в начале строки
        :return final_result (str): возвращаем найденный ключ
        """
        if not cur_str:
            cur_string = self.cur_string
        else:
            cur_string = cur_str
        final_result = ''
        search_pattern = r'^( *\.*([A-Za-z][A-Za-z0-9_]*)\s*(?=\:))'
        search_result = re.search(pattern=search_pattern, string=cur_string)
        if search_result:
            final_result = cur_string[search_result.start(): search_result.end()]
        return final_result

    def raw_data_dictionary_forming(self):
        """
            Метод формирования словаря содержащего ключи первого уровня и значения этих ключей, в виде необработанных
            ниже находящихся строк относящихся к этим ключам. Кроме этого метод формирует вложенный словарь
            комментариев, содержащий заголовок и описания к файлу, комментарии к ключам первого уровня
            Переменные:
                file: переменная хранящая ссылку на дескриптор открытого файла с данными для декодирования
                raw_data_dict (dict): переменная хранящая ссылку на формируемый словарь с сырыми данными
            :return:
                метод ничего не возвращает, результат  сохраняется в значении атрибута self.raw_data_dict
        """
        file = self.file
        raw_data_dict = self.raw_data_dict

        cur_first_level_key = ''
        equal_sign_found = False
        file_comment_framing = 0
        unallocated_file_comment_lines = ''
        header_str = ''
        top_file_description = ''
        bottom_file_description = ''
        previous_primary_key = ''
        for n, string_content in enumerate(file):
            # если есть найденный ключ
            if cur_first_level_key:
                previous_str = self.cur_string
                self.cur_string = string_content
                primary_key_search_res = self.primary_keys_searching()
                if primary_key_search_res:
                    previous_primary_key = self.cur_primary_key
                    self.cur_primary_key = cur_first_level_key = primary_key_search_res
                    if self.temp_string:
                        raw_data_dict['keys_comments'][cur_first_level_key] = \
                            {'own_comments': [self.temp_string.rstrip('\n'), '']}
                        self.temp_string = ''
                    bottom_file_description = ''
                    a = raw_data_dict['keys_comments']
                    raw_data_dict[cur_first_level_key] = []
                    string_remainder = self.string_remainder_searching(cur_first_level_key)
                    if string_remainder:
                        raw_data_dict[cur_first_level_key].append(string_remainder)
                else:
                    comment_string_searching_res = self.comment_string_searching()
                    if comment_string_searching_res and not bottom_file_description:
                        bottom_file_description += string_content.strip()
                        self.temp_string = string_content
                    elif comment_string_searching_res:
                        bottom_file_description += string_content
                        self.temp_string = string_content
                    elif bottom_file_description:
                        bottom_file_description += string_content
                        self.temp_string = ''
                    elif not bottom_file_description:
                        string_content = string_content.replace('\n', '')
                        self.temp_string = ''
                        if string_content:
                            raw_data_dict[self.cur_primary_key].append(string_content)
            # если нет ключа и не найдено обрамление заголовка и нет неопредел. строк комментариев к файлу
            elif not cur_first_level_key and file_comment_framing == 0 and not unallocated_file_comment_lines:
                self.cur_string = string_content
                file_comment_framing_search_res = self.searching_of_file_comment_framing()
                primary_key_search_res = self.primary_keys_searching()
                if primary_key_search_res:
                    self.cur_primary_key = cur_first_level_key = primary_key_search_res
                    raw_data_dict['keys_comments'][cur_first_level_key] = {'own_comments': ['', '']}
                    raw_data_dict[cur_first_level_key] = []
                    string_remainder = self.string_remainder_searching(cur_first_level_key)
                    if string_remainder:
                        raw_data_dict[cur_first_level_key].append(string_remainder)
                elif file_comment_framing_search_res:
                    file_comment_framing += 1
                    header_str += string_content
                else:
                    unallocated_file_comment_lines += string_content
            # если нет ключа и не найдено обрамление заголовка и есть не определ. строк комментариев к файлу
            elif not cur_first_level_key and file_comment_framing == 0 and unallocated_file_comment_lines:
                previous_str = self.cur_string
                self.cur_string = string_content
                file_comment_framing_search_res = self.searching_of_file_comment_framing()
                primary_key_search_res = self.primary_keys_searching()
                if primary_key_search_res:
                    self.cur_primary_key = cur_first_level_key = primary_key_search_res
                    primary_key_comment = previous_str
                    raw_data_dict['keys_comments'][cur_first_level_key] = {'own_comments': [primary_key_comment, '']}
                    previous_str_len = len(previous_str)
                    previous_str = ''
                    top_file_description = unallocated_file_comment_lines[0:-previous_str_len]
                    raw_data_dict['keys_comments']['own_comments'][1] = top_file_description
                    raw_data_dict[cur_first_level_key] = []
                    string_remainder = self.string_remainder_searching(cur_first_level_key)
                    if string_remainder:
                        raw_data_dict[cur_first_level_key].append(string_remainder)
                elif file_comment_framing_search_res:
                    file_comment_framing += 1
                    header_str += unallocated_file_comment_lines + string_content
                    unallocated_file_comment_lines = ''
                    previous_str = ''
                else:
                    unallocated_file_comment_lines += string_content
                    previous_str = ''
            # если нет ключа и есть найденное первое обрамление
            elif not cur_first_level_key and file_comment_framing == 1:
                previous_str = self.cur_string
                self.cur_string = string_content
                file_comment_framing_search_res = self.searching_of_file_comment_framing()
                primary_key_search_res = self.primary_keys_searching()
                if primary_key_search_res:
                    self.cur_primary_key = cur_first_level_key = primary_key_search_res
                    primary_key_comment = previous_str
                    raw_data_dict['keys_comments'][cur_first_level_key] = {'own_comments': [primary_key_comment, '']}
                    previous_str_len = len(previous_str)
                    previous_str = ''
                    top_file_description = header_str[0:-previous_str_len]
                    raw_data_dict['keys_comments']['own_comments'][1] = top_file_description
                    raw_data_dict[cur_first_level_key] = []
                    string_remainder = self.string_remainder_searching(cur_first_level_key)
                    if string_remainder:
                        raw_data_dict[cur_first_level_key].append(string_remainder)
                elif file_comment_framing_search_res:
                    file_comment_framing += 1
                    raw_data_dict['keys_comments']['own_comments'][0] = header_str + string_content
                    header_str = ''
                else:
                    header_str += string_content
                    previous_str = ''
            # если нет ключа и есть найденное второе обрамление
            elif not cur_first_level_key and file_comment_framing == 2:
                previous_str = self.cur_string
                comment_string_searching_res = self.comment_string_searching()
                self.cur_string = string_content
                file_comment_framing_search_res = self.searching_of_file_comment_framing()
                primary_key_search_res = self.primary_keys_searching()
                if primary_key_search_res:
                    self.cur_primary_key = cur_first_level_key = primary_key_search_res
                    if comment_string_searching_res:
                        primary_key_comment = previous_str.rstrip('\n')
                    else:
                        primary_key_comment = ''
                    raw_data_dict['keys_comments'][cur_first_level_key] = {'own_comments': [primary_key_comment, '']}
                    previous_str_len = len(previous_str)
                    previous_str = ''
                    top_file_description = top_file_description[0:-previous_str_len]
                    raw_data_dict['keys_comments']['own_comments'][1] = top_file_description
                    raw_data_dict[cur_first_level_key] = []
                    string_remainder = self.string_remainder_searching(cur_first_level_key)
                    if string_remainder:
                        raw_data_dict[cur_first_level_key].append(string_remainder)
                elif file_comment_framing_search_res:
                    file_comment_framing += 1
                    top_file_description += string_content
                    raw_data_dict['keys_comments']['own_comments'][1] = top_file_description
                    top_file_description = ''
                    previous_str = ''
                    self.cur_primary_key = cur_first_level_key = 'unclear'
                    raw_data_dict[cur_first_level_key] = []
                else:
                    top_file_description += string_content
                    previous_str = ''
        if bottom_file_description:
            raw_data_dict['keys_comments']['own_comments'][2] = bottom_file_description
        self.raw_data_dict = raw_data_dict

    def searching_of_file_comment_framing(self):
        """
            Метод поиска обрамления комментариев к файлу
        :return:
        """
        cur_string = self.cur_string
        pattern = r'[#]{25,}'
        comment_framing_searching_result = re.search(pattern=pattern, string=cur_string)
        if comment_framing_searching_result:
            return True
        else:
            return False

    def primary_keys_searching(self):
        """
            Метод поиска ключей первого уровня
        :return:
        """
        cur_string = self.cur_string
        searching_root_section_names_regex = r'^(\s*|[a-zA-Z_])[a-zA-Z0-9_]*\s*(?==)'
        key_search_result = re.search(searching_root_section_names_regex, cur_string)
        if key_search_result:
            primary_key = cur_string[key_search_result.start():key_search_result.end()]
        else:
            primary_key = ''
        return primary_key

    def comment_string_searching(self):
        """
            Метод поиска строки являющейся комментарием
        :return: True or False
        """
        cur_sting = self.cur_string
        pattern = r'^\s*#.*'
        comment_string_searching_res = re.search(pattern=pattern, string=cur_sting)
        if comment_string_searching_res:
            return True
        else:
            return False

    def string_remainder_searching(self, primary_key):
        """
            Метод поиска остатка строки после ключа первого уровня
        :param primary_key:
        :return:
        """
        cur_string = self.cur_string
        pattern = r'(?<=' + primary_key + r').+'
        string_remainder_searching_res = re.search(pattern=pattern, string=cur_string)
        if string_remainder_searching_res:
            search_string = cur_string[string_remainder_searching_res.start(): string_remainder_searching_res.end()]
            search_string = search_string.strip('\n')
            search_string = search_string.strip()
            search_string = search_string.strip('=')
            search_string = search_string.strip()
        else:
            search_string = ''
        return search_string


class SdDataEncoding:
    def __init__(self, file_path, source_dictionary):
        self.file_path = file_path
        self.source_dictionary = source_dictionary
        self.file = None

    def sd_data_encoding_management(self):
        source_dictionary = self.source_dictionary
        with io.StringIO() as self.file:
            check_the_first_rec = True
            comments_dictionary = False
            if 'keys_comments' in source_dictionary:
                comments_dictionary = True
            if comments_dictionary and 'own_comments' in source_dictionary['keys_comments'] and \
                    source_dictionary['keys_comments']['own_comments'][0]:
                entry_string = '######################################################################################' \
                               '##############\n# ' + source_dictionary['keys_comments']['own_comments'][0] + \
                               '\n###################################################################################' \
                               '#################\n'
                self.file.write(entry_string)
                if source_dictionary['keys_comments']['own_comments'][1]:
                    entry_string = '#\n' + source_dictionary['keys_comments']['own_comments'][1]

                    entry_string = re.sub(r'(\n)', '\n# ', entry_string)
                    entry_string += '\n#\n#############################################################################' \
                                    '#######################\n'
                    self.file.write(entry_string)
                self.file.write('\n\n')
            else:
                self.file.write('######################################################################################'
                                '##############'
                                '\n# Данные в формате .sd\n'
                                '######################################################################################'
                                '##############'
                                '\n')
                if 'version' in globals():
                    self.file.write('#\n'
                                    '# Версия модуля: ' + version + '\n'
                                                                    '#\n'
                                                                    '#################################################################################'
                                                                    '###################'
                                                                    '\n\n')
                else:
                    self.file.write('#\n'
                                    '# Версия модуля: ------- \n'
                                    '#\n'
                                    '#################################################################################'
                                    '###################'
                                    '\n\n')
            for main_key in source_dictionary:
                if main_key == 'keys_comments':
                    continue
                if comments_dictionary and \
                        main_key in source_dictionary['keys_comments'] and \
                        source_dictionary['keys_comments'][main_key]['own_comments'][0]:
                    if not check_the_first_rec:
                        self.file.write("\n")
                        check_the_first_rec = False
                    top_comment = '# ' + source_dictionary['keys_comments'][main_key]['own_comments'][0]
                    self.file.write(top_comment + '\n')

                if source_dictionary[main_key] == '':
                    main_key_row = main_key + ' ='
                    main_key_row += ' ' + source_dictionary[main_key]
                    if comments_dictionary and source_dictionary['keys_comments'][main_key]['own_comments'][1]:
                        main_key_row += '    # ' + source_dictionary['keys_comments'][main_key]['own_comments'][1]
                    self.file.write(main_key_row + '\n')
                    check_the_first_rec = False
                elif isinstance(source_dictionary[main_key], str):
                    check_colon_of_the_end = re.search(r':$', source_dictionary[main_key])
                    if '\n' in source_dictionary[main_key]:
                        main_key_row = main_key + '='
                        if comments_dictionary and source_dictionary['keys_comments'][main_key]['own_comments'][1]:
                            main_key_row += '    # ' + source_dictionary['keys_comments'][main_key]['own_comments'][1]
                        self.file.write(main_key_row + '\n')
                        self.file.write("'''\n")
                        self.file.write(source_dictionary[main_key] + '\n')
                        self.file.write("'''\n\n")
                    elif ' ' in source_dictionary[main_key] or ',' in source_dictionary[main_key] or \
                            check_colon_of_the_end:
                        check_colon_of_the_end = None
                        main_key_row = main_key + '='
                        main_key_row += ' """' + source_dictionary[main_key] + '"""'
                        if comments_dictionary and main_key in source_dictionary['keys_comments'] and \
                                'own_comments' in source_dictionary['keys_comments'][main_key] and \
                            source_dictionary['keys_comments'][main_key]['own_comments'][1]:
                            main_key_row += '    # ' + source_dictionary['keys_comments'][main_key]['own_comments'][1]
                        self.file.write(main_key_row + '\n')
                        check_the_first_rec = False
                    else:
                        main_key_row = main_key + '='
                        main_key_row += ' ' + source_dictionary[main_key]
                        if comments_dictionary and source_dictionary['keys_comments'][main_key]['own_comments'][1]:
                            main_key_row += '    # ' + source_dictionary['keys_comments'][main_key]['own_comments'][1]
                        self.file.write(main_key_row + '\n')
                        check_the_first_rec = False
                elif isinstance(source_dictionary[main_key], list):
                    main_key_row = main_key + '= '
                    sum_of_the_lengths_check = self.sum_of_the_lengths_checking(main_key)
                    nested_list_check = self.checking_for_a_nested_list(main_key)
                    if sum_of_the_lengths_check and not nested_list_check:
                        for el in source_dictionary[main_key]:
                            el = str(el)
                            check_colon_of_the_end = re.search(r':$', el)
                            if ' ' in el or ',' in el or '\n' in el or check_colon_of_the_end:
                                el = '"""' + el + '"""'
                                check_colon_of_the_end = None
                            main_key_row += el + ', '
                        len_list = len(main_key_row)
                        main_key_row = main_key_row[:len_list - 2]
                        if comments_dictionary and source_dictionary['keys_comments'][main_key]['own_comments'][1]:
                            main_key_row += '    # ' + source_dictionary['keys_comments'][main_key]['own_comments'][1]
                        self.file.write(main_key_row + '\n')
                        check_the_first_rec = False
                    else:
                        if comments_dictionary and source_dictionary['keys_comments'][main_key]['own_comments'][1]:
                            main_key_row += '    # ' + source_dictionary['keys_comments'][main_key]['own_comments'][1]
                        main_key_row += self.multiline_list_representation(main_key)
                        self.file.write(main_key_row + '\n')
                        check_the_first_rec = False
                elif isinstance(source_dictionary[main_key], dict):
                    single_level_dictionary = True
                    for key, el in source_dictionary[main_key].items():
                        if isinstance(el, dict) or isinstance(el, list):
                            single_level_dictionary = False
                            break
                    if single_level_dictionary:
                        main_key_row = main_key + '= '
                        for key, el in source_dictionary[main_key].items():
                            el = str(el)
                            if ' ' in el or ',' in el or '\n' in el:
                                el = '"""' + el + '"""'
                            main_key_row += key + ': ' + el + ', '
                        len_list = len(main_key_row)
                        main_key_row = main_key_row[:len_list - 2]
                        if comments_dictionary and source_dictionary['keys_comments'][main_key]['own_comments'][1]:
                            main_key_row += '    # ' + source_dictionary['keys_comments'][main_key]['own_comments'][1]
                        self.file.write(main_key_row + '\n')
                        check_the_first_rec = False
                    else:
                        main_key_row = main_key + '='
                        if comments_dictionary and source_dictionary['keys_comments'][main_key]['own_comments'][1]:
                            main_key_row += '    # ' + source_dictionary['keys_comments'][main_key]['own_comments'][1] \
                                            + '\n'
                        else:
                            main_key_row += '\n'
                        number_of_dots = 1
                        if comments_dictionary and source_dictionary['keys_comments'][main_key]:
                            dict_slice = source_dictionary['keys_comments'][main_key]
                        else:
                            dict_slice = False
                        main_key_row += self.multiline_dictionary_representation(cur_dict=source_dictionary[main_key],
                                                                                 number_of_dots=number_of_dots,
                                                                                 comments_dict=dict_slice)
                        main_key_row += '\n'
                        self.file.write(main_key_row)
            if comments_dictionary and 'own_comments' in source_dictionary['keys_comments'] and \
                    source_dictionary['keys_comments']['own_comments'][2]:
                entry_string = source_dictionary['keys_comments']['own_comments'][2].lstrip()
                entry_string = '#\n' + entry_string
                entry_string = re.sub(r'(\n)', '\n# ', entry_string)
                entry_string = '\n\n##################################################################################' \
                               '#################\n' + entry_string
                entry_string += '\n#\n#############################################################################' \
                                '#######################\n'
                self.file.write(entry_string)

            with open(self.file_path, mode='w', encoding='utf-8') as f:
                self.file.seek(0)
                str_slice = self.file.read(16384)
                while str_slice:
                    f.write(str_slice)
                    str_slice = self.file.read(16384)




    def sum_of_the_lengths_checking(self, cur_key):
        """
            Метод проверки суммы длин значений списка. Метод проверяет не превышает ли сумма длин значений списка 100
            знаков.
            :param cur_key: текущий ключ первого уровня
            :return: False если сумма свыше 100 знаков или True
        """
        source_dictionary = self.source_dictionary
        sum_of_the_lengths = 0
        for el in source_dictionary[cur_key]:
            sum_of_the_lengths += len(str(el))
            if sum_of_the_lengths > 100:
                return False
        if sum_of_the_lengths <= 100:
            return True

    def checking_for_a_nested_list(self, cur_key):
        """
            Метод проверяет список на наличие вложенного списка
            :param cur_key: текущий ключ верхнего уровня
            :return: True если обнаружен вложенный список, иначе False
        """
        source_dictionary = self.source_dictionary
        for el in source_dictionary[cur_key]:
            if isinstance(el, list):
                return True
        return False

    def multiline_list_representation(self, cur_key):
        """
            Метод формирования части строки, содержащей многострочную запись списка
            :param cur_key: текущий ключ
            :return: Метод возвращает часть строки
        """
        source_dictionary = self.source_dictionary
        string_part = '\n---\n'
        for el in source_dictionary[cur_key]:
            if isinstance(el, list):
                for e in el:
                    e = str(e)
                    if ' ' in e or ',' in e or '\n' in e:
                        e = '"""' + e + '"""'
                    string_part += e + ', '
                len_list = len(string_part)
                string_part = string_part[:len_list - 2]
                string_part += '\n'
            else:
                el = str(el)
                if ' ' in el or ',' in el or '\n' in el:
                    el = '"""' + el + '"""'
                string_part += el + '\n'
        string_part += '---\n'
        return string_part

    def multiline_dictionary_representation(self, cur_dict, number_of_dots, comments_dict=None):
        source_dictionary = cur_dict
        comments_dictionary = comments_dict
        string_part = ''
        for key, value in cur_dict.items():
            n = 0
            while n < number_of_dots:
                string_part += '.'
                n += 1
            string_part += key + ':'
            if isinstance(value, dict):
                num_of_dots = number_of_dots + 1
                if comments_dictionary and comments_dictionary[key]:
                    dict_slice = comments_dictionary[key]
                else:
                    dict_slice = False
                if comments_dictionary and comments_dictionary[key]['own_comments'][1]:
                    string_part += '    # ' + comments_dictionary[key]['own_comments'][1]
                string_part += '\n'
                string_part += self.multiline_dictionary_representation(value, num_of_dots, dict_slice)
            else:
                string_part += ' '
                if isinstance(value, str):
                    if ' ' in source_dictionary[key] or ',' in source_dictionary[key]:
                        string_part += ' """' + value + '"""'
                        if comments_dictionary and key in comments_dictionary and \
                                comments_dictionary[key]['own_comments'][1]:
                            string_part += '    # ' + comments_dictionary[key]['own_comments'][1] + '\n'
                        else:
                            string_part += '\n'
                    else:
                        string_part += value
                        if comments_dictionary and key in comments_dictionary \
                                and comments_dictionary[key]['own_comments'][1]:
                            string_part += '    # ' + comments_dictionary[key]['own_comments'][1] + '\n'
                        else:
                            string_part += '\n'
                elif isinstance(value, list):
                    if not value:
                        string_part += '\n'
                    for el in value:
                        el = str(el)
                        if ' ' in el or ',' in el or '\n' in el:
                            el = '"""' + el + '"""'
                        string_part += el + ', '
                    len_str = len(string_part)
                    string_part = string_part[:len_str - 2]
                    if comments_dictionary and key in comments_dictionary and \
                            comments_dictionary[key]['own_comments'][1]:
                        string_part += '    # ' + comments_dictionary[key]['own_comments'][1] + '\n'
                    else:
                        string_part += '\n'
                # else:
                #     string_part += ':\n'
        return string_part


service_data_conversion = ServiceDataConversion
sd = ServiceDataConversion
