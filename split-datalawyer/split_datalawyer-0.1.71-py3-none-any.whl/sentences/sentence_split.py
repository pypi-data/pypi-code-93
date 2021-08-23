import pandas as pd
import re
import html

import stanza

from split_datalawyer.modules.modules_types import ModulesType
from split_datalawyer.sentences.split_utils import split
from split_datalawyer.utils import ABBREVIATION_LIST, CONTINUATION_TERMS, get_stop_patterns
from split_datalawyer.utils.utils import parenthesis_is_closed

__ENDING_PUNCTUATION_TUPLE__ = tuple([".", ";", ":", "\"", "!", "?", ")"])
__ALPHA_SECTION_NUMBER__ = re.compile(r"^[a-zA-Z]{1}\s*[\.\-\)]+")
__REGEX_SECTION_NUMBERS__ = [re.compile(r"^[0-9]{1,}(\.[0-9]+)?[\.\-\)\s]+$"),  # "1.0.", "4.2.", "02.-"
                             re.compile(r"^[0-9]{1,}(\.[0-9]+)+[\.\-\)]*$"),  # "4.9"
                             re.compile(r"^([\.\-]*[MDCLXVI]{1,4}\s*[\.\-\)]?)$", re.IGNORECASE),  # "I.", "II."
                             re.compile(r"^(\([MDCLXVI]{1,4}\s*\))$", re.IGNORECASE),  # "(I)", "(ii)"
                             re.compile(r"^\(?[a-zA-Z]{1}\)?$"),
                             __ALPHA_SECTION_NUMBER__]  # "i)", "a)", "a-", "(i)"
__DECIMAL_NUMBERS__ = re.compile(r"^[-+]?(?:\b[0-9]+(?:[,.]?[0-9]{3})*[,.][0-9]{2}\b)")
__OAB_NUMBER__ = re.compile(r"^(?:[0-9]+(?:[.]?[0-9]{3})*)$")
__LAW_NUMBERS__ = [re.compile(r"^(?:[0-9]+(?:[.][0-9]{3})+(?:[\/][0-9]{2,4})*)$")]

__SECTION_NUMBER__ = re.compile(r"^[0-9]{1,}(\.[0-9]+)?[\.\-\)]*$")  # "1.0.", "4.2.", "02.-, 1.0, 1-"
__CNJ_NUMBER__ = re.compile(r"\d{7}\-\d{2}\.\d{4}\.\d{1}\.\d{2}\.\d{4}")


class SentenceSplit:

    def __init__(self, stop_patterns_path=None, debug_log=False, modules=[]):
        self._list_stop_patterns = get_stop_patterns(stop_patterns_path)
        self._list_abbreviations = ABBREVIATION_LIST
        self._ending_abbreviations = ['etc']
        self._stanza_model = None
        self._debug_log = debug_log
        self._debug_messages = []
        self._modules = modules

    def _log(self, message):
        if self._debug_log:
            self._debug_messages.append(message)

    def _get_models_by_type(self, module_type):
        modules = []

        for module in self._modules:
            if module.get_type() == module_type:
                modules.append(module)

        return modules

    def _must_remove_duplicated(self, remove_duplicated, document_sentences):
        if remove_duplicated:
            return remove_duplicated

        must_remove = False
        conditional_modules = self._get_models_by_type(ModulesType.DUPLICATED_CONDITION)

        for module in conditional_modules:
            must_remove = must_remove and module.evaluate(document_sentences)

        return must_remove

    def generate_log(self):
        if self._debug_log:
            with open("sentence_split_log.txt", mode='w', encoding='utf8') as log_file:
                for message in self._debug_messages:
                    log_file.write(message + "\n")

    def _ends_with_ending_abbreviation(self, text: str) -> bool:
        return any([text.endswith(f'{ending_abbreviation}.') for ending_abbreviation in self._ending_abbreviations])

    def _ends_with_abbreviation(self, text: str) -> bool:
        if text.startswith(tuple(["(", "\""])):
            text = text[1:]
        reference = text.strip().lower()
        return not self._ends_with_ending_abbreviation(reference) and reference in self._list_abbreviations

    def _end_with_continuation(self, text: str):
        return any(len(regex.findall(text)) > 0 for regex in CONTINUATION_TERMS)

    def _is_cnj_number(self, text: str) -> bool:
        return len(__CNJ_NUMBER__.findall(text)) > 0

    def _is_oab_number(self, text: str) -> bool:
        return len(__OAB_NUMBER__.findall(text)) > 0

    def _is_law_number(self, text: str) -> bool:
        return any(regex.match(text) for regex in __LAW_NUMBERS__)

    def _ends_with_law_number(self, text: str) -> bool:
        return self._is_law_number(text.split()[-1])

    def _is_section_number(self, text: str) -> bool:
        return not self._is_cnj_number(text) and any(regex.match(text) for regex in __REGEX_SECTION_NUMBERS__)

    def _starts_with_section_number(self, text: str) -> bool:
        return self._is_section_number(text.split()[0])

    def _is_alpha_section_number(self, text: str) -> bool:
        return len(__ALPHA_SECTION_NUMBER__.findall(text)) > 0

    def _is_upper(self, text: str) -> bool:
        return re.sub(r'[ªº]', '', text).isupper() and len(text) > 1

    def _is_pair_key_value_line(self, text: str) -> bool:
        return not self._ends_with_punctuation(text) and len(text.split(':')) == 2

    def _starts_with_decimal(self, text: str) -> bool:
        if len(__DECIMAL_NUMBERS__.findall(text)) > 0:
            matches = __SECTION_NUMBER__.findall(text)
            if len(matches) == 0 or all([len(match) == 0 for match in matches]):
                return True
        return False

    def _starts_with_comma(self, text: str) -> bool:
        return text.startswith(",") and text.strip() != ","

    def _should_concat_with_previous(self, text: str, previous_text: str):
        return self._starts_lower(previous_text) and not self._starts_with_section_number(previous_text) and \
               (
                       not self._ends_with_punctuation(text) and not self._is_upper(text) and
                       not self._is_pair_key_value_line(text) and not self._is_oab_signature(text)
               )

    def _starts_with_parenthesis(self, text: str) -> bool:
        return text.startswith("(") and not self._starts_with_section_number(text)

    def _is_oab_signature(self, text: str) -> bool:
        return "OAB" in text and self._is_oab_number(text.split()[-1])

    def _concat_inverted_phrases(self, df):
        df = df[df['final_text'] != ""]
        df = df.sort_values('index').reset_index(drop=True)

        for i in range(1, len(df['final_text'])):
            previous_text = df['final_text'][i - 1]
            current_text = df['final_text'][i]

            if current_text != "":
                if i + 1 < len(df['final_text']):
                    next_text = df['final_text'][i + 1]

                    previous_has_end = self._ends_with_punctuation(previous_text)
                    current_text_starts_lower = self._starts_lower(current_text)
                    current_text_has_end = self._ends_with_punctuation(current_text)
                    next_has_not_end = not self._ends_with_punctuation(next_text)
                    next_text_is_not_option = re.match(r"^\w\)", next_text) is None
                    next_is_not_all_upper = not self._is_upper(next_text)

                    if current_text_starts_lower and current_text_has_end and \
                            previous_has_end and next_has_not_end and \
                            next_text_is_not_option and next_is_not_all_upper:
                        df.at[i + 1, 'final_text'] = next_text + " " + current_text
                        df.at[i, 'final_text'] = ""
                        self._log("_concat_inverted_phrases: " + next_text + " " + current_text)
                    elif self._should_concat_with_previous(current_text, previous_text):
                        df.at[i, 'final_text'] = current_text + " " + previous_text
                        df.at[i - 1, 'final_text'] = ""
                        self._log("_concat_inverted_phrases: " + current_text + " " + previous_text)

        return df

    def _ends_with_punctuation(self, text: str) -> bool:
        if len(text) > 0:
            tokens = text.split()
            last_token_html_entity = (tokens[-1].startswith('&') or tokens[-1].startswith('\\&')) and tokens[
                -1].endswith(
                ';')
            return text.endswith(__ENDING_PUNCTUATION_TUPLE__) and not last_token_html_entity
        return False

    def _starts_lower(self, text: str) -> bool:
        return len(text) > 0 and text[0].islower()

    def _concat_broken_phrases(self, df, split_parenthesis_ending: bool = False):
        df['final_text'] = df['text']
        last_index_with_text = None

        for i in range(len(df['final_text'])):
            current_text = df['final_text'][i].strip()

            if current_text == "":
                continue

            if current_text == ",":
                df.at[i, 'final_text'] = ""
                continue

            all_text_upper = self._is_upper(current_text)

            if last_index_with_text is not None:
                last_text_processed = df['final_text'][last_index_with_text]

                is_last_section_number = self._is_section_number(last_text_processed)
                last_text_end_punctuation = self._ends_with_punctuation(
                    last_text_processed) and not self._ends_with_abbreviation(last_text_processed.split()[-1])
                starts_money_symbol = current_text.startswith("R$") and last_text_end_punctuation
                starts_with_parenthesis = self._starts_with_parenthesis(
                    current_text) and last_text_end_punctuation and not split_parenthesis_ending
                starts_with_comma = self._starts_with_comma(current_text)  # and last_text_end_punctuation
                starts_with_decimal = self._starts_with_decimal(
                    current_text.split()[0])  # and last_text_end_punctuation
                if last_index_with_text - 1 >= 0:
                    text_before_last = df['final_text'][last_index_with_text - 1]
                    before_ended_with_colon = text_before_last.endswith(':') and len(text_before_last.split()) <= 2
                else:
                    before_ended_with_colon = False
                # starts_with_lower = self._starts_lower(current_text)

                if starts_money_symbol or starts_with_parenthesis or (
                        is_last_section_number and not before_ended_with_colon and len(last_text_processed.split()) <= 1
                ) or starts_with_comma or starts_with_decimal:  # or starts_with_lower:
                    separator = "" if starts_with_decimal and last_text_end_punctuation else " "
                    current_text = separator.join([last_text_processed, current_text])
                    df.at[i, 'final_text'] = current_text
                    df.at[last_index_with_text, 'final_text'] = ""

                elif self._should_concat_with_previous(current_text, last_text_processed):
                    current_text = current_text + " " + last_text_processed
                    df.at[i, 'final_text'] = current_text
                    df.at[i - 1, 'final_text'] = ""

            current_starts_section_number = self._starts_with_section_number(current_text)
            is_current_incomplete_section_number = current_starts_section_number and len(current_text.split()) == 1
            current_ends_with_punctuation = is_current_incomplete_section_number or self._ends_with_punctuation(
                current_text)
            current_text_ends_with_abbreviation = self._ends_with_abbreviation(current_text.split()[-1])
            parenthesis_not_closed = not parenthesis_is_closed(current_text)
            search_phrase_continuation = (
                                                 is_current_incomplete_section_number or
                                                 (
                                                         not current_ends_with_punctuation and
                                                         not all_text_upper and
                                                         not self._starts_with_decimal(current_text.split()[-1]) and
                                                         not self._ends_with_law_number(current_text) and
                                                         not self._is_oab_signature(current_text)
                                                 )
                                         ) or parenthesis_not_closed or current_text_ends_with_abbreviation
            phrase_has_continuation = False

            if search_phrase_continuation:
                phrases_parts_index = []
                previous_phrase_index = 1
                waiting_close_parenthesis = parenthesis_not_closed

                for j in range(i + 1, len(df['final_text'])):
                    next_text = df['final_text'][j].strip()
                    if next_text == "":
                        previous_phrase_index = previous_phrase_index + 1
                        continue

                    # previous_incomplete_section_number = False
                    previous_ends_with_continuation = False
                    previous_text_end_with_abbreviation = False

                    if j - previous_phrase_index >= 0:
                        previous_text = df['final_text'][j - previous_phrase_index]
                        if previous_text != "":
                            previous_end = previous_text.split()[-1]

                            # previous_incomplete_section_number = self._starts_with_section_number(
                            #     previous_text) and len(previous_text.split()) == 1
                            previous_ends_with_continuation = self._end_with_continuation(previous_text)
                            previous_text_end_with_abbreviation = self._ends_with_abbreviation(previous_end)

                    # Not allow concatenate parts with high difference distance.
                    parts_not_too_long_distance = ((len(phrases_parts_index) > 0) and
                                                   max(phrases_parts_index) - j <= 5) \
                                                  or (j - i <= 5)

                    next_start_token = next_text.split()[0]

                    is_next_section_number = next_start_token != 'p.' and self._is_alpha_section_number(
                        next_start_token)

                    if parts_not_too_long_distance and not is_next_section_number and \
                            (
                                    self._ends_with_abbreviation(next_text) or  # or is_next_section_number
                                    self._starts_lower(next_start_token) or
                                    # previous_incomplete_section_number or
                                    previous_ends_with_continuation or
                                    previous_text_end_with_abbreviation or
                                    waiting_close_parenthesis
                            ):

                        phrases_parts_index.append(j)
                        next_text_end_not_with_abbreviation = not self._ends_with_abbreviation(next_text.split()[-1])

                        waiting_close_parenthesis = not parenthesis_is_closed(next_text)

                        if self._ends_with_punctuation(next_text) and \
                                next_text_end_not_with_abbreviation and \
                                waiting_close_parenthesis:
                            self._log("waiting_close_parenthesis: " + df['final_text'][j])

                        go_concatenate = (
                                                 self._ends_with_punctuation(next_text) or
                                                 self._starts_with_decimal(next_text.split()[-1])
                                         ) and next_text_end_not_with_abbreviation
                        if go_concatenate:
                            phrase_has_continuation = True
                            break
                    else:
                        if len(phrases_parts_index) > 0:
                            phrase_parts_log = [df['final_text'][index] for index in phrases_parts_index]
                            phrase_parts_log = "[" + "| ".join(phrase_parts_log) + "]"

                            if (len(phrases_parts_index) >= 3) or parenthesis_not_closed:
                                phrase_has_continuation = True
                                self._log("_concat_broken_phrases: threshold pass: " + phrase_parts_log)
                            else:
                                self._log(
                                    "_concat_broken_phrases: ignored_parts: " + phrase_parts_log + " next_text: " + next_text)

                        break

                end_of_phrase = ""
                if phrase_has_continuation:
                    for part_index in phrases_parts_index:
                        phrase_part = df['final_text'][part_index]
                        end_of_phrase = end_of_phrase + " " + phrase_part
                        df.at[part_index, 'final_text'] = ""

                    if end_of_phrase != "":
                        df.at[i, 'final_text'] = current_text + " " + end_of_phrase.strip()

            last_index_with_text = i

        return df

    def _remove_small_phrases(self, df, minimium_word_count=3):
        if minimium_word_count > 0:
            df['final_text'] = df['text']

            for i in range(len(df['final_text'])):
                phrase_is_small = len(df['final_text'][i].split()) < minimium_word_count

                if phrase_is_small:
                    df.at[i, 'final_text'] = ""

        return df

    def _remove_stop_phrases(self, df):
        if df.empty:
            return None

        for i, row in df.iterrows():
            current_value = row['text']
            is_number_page = current_value.isdigit()
            if is_number_page:
                self._log("is_number_page: " + current_value)
            is_stop_phrase = any(regex.match(current_value) for regex in self._list_stop_patterns)
            remove_text = is_number_page or is_stop_phrase
            if remove_text:
                df.at[i, 'text'] = ""
        df = df[df['text'] != ""].reset_index(drop=True, inplace=False)
        return df

    def _remove_duplicates(self, df):
        df = df[df['final_text'] != ""]
        df = df.sort_values(['final_text', 'index']).reset_index(drop=True)
        duplicated_phrases = list(df[df['duplicated']]['final_text'])
        self._log("_remove_duplicates: duplicated_phrases: [" + '| '.join(duplicated_phrases) + "]")

        previous_value = ""
        phrases_count = len(df['final_text'])
        for i in range(phrases_count):
            reserve_index = phrases_count - i - 1
            current_value = df['final_text'][reserve_index]

            both_equals = previous_value == current_value

            if both_equals:
                df.at[reserve_index, 'final_text'] = ""

            if df['final_text'][reserve_index] != "":
                previous_value = df['final_text'][reserve_index]

        df = df[df['final_text'] != ""]
        df = df.sort_values('index').reset_index(drop=True)

        return df

    def _split_by_punctuation(self, df, split_by_semicolon: bool, split_parenthesis_ending: bool = False,
                              split_by_hyphens: bool = False, limit: int = 500):
        column_name = 'text'

        if "final_text" in df.columns:
            column_name = 'final_text'

        df = df[df[column_name] != ""].reset_index(drop=True, inplace=False)

        return df

    def get_sentences(self, text, remove_duplicated=True, concat_phrases=True, concat_inverted_phrases=True,
                      remove_stop_phrases=True, minimum_word_count=0, split_by_semicolon=True,
                      split_parenthesis_ending: bool = False,
                      split_by_hyphens: bool = False, limit: int = 500):
        if (text is None) or text == "":
            return None

        df = self.get_sentences_with_index(text,
                                           remove_duplicated=remove_duplicated,
                                           concat_phrases=concat_phrases,
                                           concat_inverted_phrases=concat_inverted_phrases,
                                           remove_stop_phrases=remove_stop_phrases,
                                           minimum_word_count=minimum_word_count,
                                           split_by_semicolon=split_by_semicolon,
                                           split_parenthesis_ending=split_parenthesis_ending,
                                           split_by_hyphens=split_by_hyphens,
                                           limit=limit)

        if df is not None:
            column_name = 'text'

            if "final_text" in df.columns:
                column_name = 'final_text'

            df = df[df[column_name] != ""].reset_index(drop=True, inplace=False)
            sentences = list(df[column_name])

            return sentences

        return []

    def _process_df_pipeline(self, df, pipeline_functions):
        for func_step in pipeline_functions:
            if df is None or df.empty:
                return None
            df = func_step(df)

        return df

    def _mark_duplicated_text(self, df):
        df['duplicated'] = df['final_text'].duplicated(False)
        return df

    def _remove_empty_rows(self, df):
        df = df[df['text'] != ""].reset_index(drop=True, inplace=False)
        return df

    def _create_sentences_data_frame(self, text, split_by_semicolon=False, split_parenthesis_ending: bool = False,
                                     split_by_hyphens: bool = False, limit: int = 500):
        text = self._preprocessing_text(text)

        if (text is None) or text == "":
            return None

        sentence_list = split(text, split_by_semicolon=split_by_semicolon,
                              split_parenthesis_ending=split_parenthesis_ending,
                              split_by_hyphens=split_by_hyphens, limit=limit)
        temp_object_list = [{'index': index, 'text': sentence_list[index]}
                            for index in range(len(sentence_list))]

        return pd.DataFrame(temp_object_list)

    def get_sentences_with_index(self, text, remove_duplicated=True, concat_phrases=True, concat_inverted_phrases=True,
                                 remove_stop_phrases=True, minimum_word_count=0, split_by_semicolon=True,
                                 split_parenthesis_ending: bool = False,
                                 split_by_hyphens: bool = False, limit: int = 500):

        df = self._create_sentences_data_frame(text, split_by_semicolon=split_by_semicolon,
                                               split_parenthesis_ending=split_parenthesis_ending,
                                               split_by_hyphens=split_by_hyphens, limit=limit)
        if df is None:
            return None

        pipeline_df_funcions = [self._remove_empty_rows]
        if remove_stop_phrases:
            pipeline_df_funcions.append(self._remove_stop_phrases)

        df = self._process_df_pipeline(df, pipeline_df_funcions)

        if df is None:
            return None

        df = self._split_by_punctuation(df=df, split_by_semicolon=split_by_semicolon,
                                        split_parenthesis_ending=split_parenthesis_ending,
                                        split_by_hyphens=split_by_hyphens, limit=limit)

        if len(df) == 0:
            return None

        if concat_phrases:
            df = self._concat_broken_phrases(df, split_parenthesis_ending=split_parenthesis_ending)
            if concat_inverted_phrases:
                df = self._concat_inverted_phrases(df)

        if self._must_remove_duplicated(remove_duplicated, df['final_text']):
            self._mark_duplicated_text(df)
            df = self._remove_duplicates(df)

        if minimum_word_count > 0:
            df = self._remove_small_phrases(df, minimum_word_count)

        df = self._remove_empty_rows(df)
        df = df.sort_values('index').reset_index(drop=True)
        df['index'] = df.index

        return df

    def get_sentences_with_stanza(self, text):
        if (text is None) or text == "":
            return None

        if self._stanza_model is None:
            stanza.download('pt')

            self._stanza_model = stanza.Pipeline('pt', processors='tokenize')

        text = re.sub("\x0C", "\n", text)
        text = text.replace("\n", " ")

        sentences_result = []

        if text != "":
            doc = self._stanza_model(text)

            sentence_to_add = ""
            for i, sentence_obj in enumerate(doc.sentences):
                sentence = sentence_obj.text

                end_with_abbreviation = self._ends_with_abbreviation(sentence.split()[-1])

                if end_with_abbreviation:
                    sentence_to_add = sentence + " "
                else:
                    sentence_to_add = sentence_to_add + sentence

                if not end_with_abbreviation:
                    sentences_result.append(sentence_to_add)
                    sentence_to_add = ""

        return sentences_result

    def _preprocessing_text(self, text):
        if (text is None) or text == "":
            return None
        text = html.unescape(text)
        replace_modules = self._get_models_by_type(ModulesType.REPLACE)
        for module in replace_modules:
            text = module.transform(text)
        return text
