from spacy import Language

from .charnormalizer import CharNormalizer
from .date2string import Date2String
from .time2string import Time2String
from .num2string import Num2String
from .abbreviation import Abbreviation
from .punctuation_remover import Punc_remover
from .affix_norm import AffixNorm
from .spell_checker import SpellCheck
from .tokenizer import Tokenizer as ParsivarTokenizer
from .mapping_words import Word_Mapper
import spacy
import os


# word and sentence tokenizer
# @Language.factory("disabletokenizer")
class WhitespaceTokenizer():
    def __init__(self, vocab):
        self.vacab = vocab

    def __call__(self, string):
        return string


# @spacy.registry.tokenizers("whitespace_tokenizer")
# def create_whitespace_tokenizer():
#     def create_tokenizer(nlp):
#         return WhitespaceTokenizer(nlp)
#
#     return create_tokenizer


# @Language.factory("CustomSentenceTokenizer")
# class CustomSentenceTokenizer():
#     def __init__(self):
#         self.tokenizer = parsivar_tokenizer()
#
#     def __call__(self, string):
#         return self.tokenizer.tokenize_sentences(string)
# nlp.tokenizer = disabletokenizer()
# nlp.tokenizer_sentence = CustomSentenceTokenizer()


# -------------------------------------------

class NormalizerClass:
    def __init__(self, nlp: Language, config_file: str):
        self.config_file = config_file
        self.normalizer = CharNormalizer(config_file)

    def __call__(self, doc):
        return self.normalizer.normalize(doc)


@Language.factory("char_normalizer", default_config={"config_file": str})
def char_normalizer(nlp: Language, name: str, config_file: str):
    return NormalizerClass(nlp, config_file)


# -----------------------------------------------------------


class DateString:
    def __init__(self, nlp: Language):
        self.date_2_string = Date2String()

    def __call__(self, doc):
        return self.date_2_string.normalize(doc)


@Language.factory("date2str", default_config={})
def date2str(nlp: Language, name: str):
    return DateString(nlp)


# -----------------------------------------------------------
class NumString:
    def __init__(self, nlp: Language):
        self.num_2_string = Num2String()

    def __call__(self, doc):
        return self.num_2_string.normalize(doc)


@Language.factory("num2str", default_config={})
def num2str(nlp: Language, name: str):
    return NumString(nlp)


# -----------------------------------------------------------
class TimeString:
    def __init__(self, nlp: Language):
        self.time_2_string = Time2String()

    def __call__(self, doc):
        return self.time_2_string.normalize(doc)


@Language.factory("time2str", default_config={})
def time2str(nlp: Language, name: str):
    return TimeString(nlp)


# -----------------------------------------------------------
class Abbreviation2Word:
    def __init__(self, nlp: Language):
        self.Abbreviation_2_word = Abbreviation()

    def __call__(self, doc):
        return self.Abbreviation_2_word.normalize(doc)


@Language.factory("abbreviation2word", default_config={})
def Abbreviation2word(nlp: Language, name: str):
    return Abbreviation2Word(nlp)


# -----------------------------------------------------------
ParsivarTokenizer = ParsivarTokenizer()


@Language.component("word_level_tokenizer")
def word_level_tokenizer(doc):
    # print("tokenize2str Process Done!")
    return ParsivarTokenizer.tokenize_words(doc)


# -----------------------------------------------------------
class PunctuationRemover:
    def __init__(self, nlp: Language):
        self.punc_remover = Punc_remover()

    def __call__(self, doc):
        return self.punc_remover.normalize(doc)


@Language.factory("punctuation_remover", default_config={})
def punctuation_remover(nlp: Language, name: str):
    return PunctuationRemover(nlp)


# -----------------------------------------------------------

class Affix2Norm:
    def __init__(self, nlp: Language, config_file: str, double_postfix_joint: bool):
        self.config_file = config_file
        self.double_postf_joint = double_postfix_joint
        self.affix = AffixNorm(self.config_file, self.double_postf_joint)

    def __call__(self, doc):
        return self.affix.normalize(doc)


@Language.factory("affix2norm", default_config={"config_file": str, "double_postfix_joint": bool})
def affix2norm(nlp: Language, name: str, config_file: str, double_postfix_joint: bool):
    return Affix2Norm(nlp, config_file, double_postfix_joint)


# -----------------------------------------------------------

class WordMapper:
    def __init__(self, nlp: Language, config_file: str, half_space_char: str):
        self.config_file = config_file
        self.half_space_char = half_space_char
        self.mapper = Word_Mapper(self.config_file, half_space_char)

    def __call__(self, doc):
        return self.mapper.normalize(doc)


@Language.factory("word_mapper", default_config={"config_file": str, "half_space_char": str})
def word_mapper(nlp: Language, name: str, config_file: str, half_space_char):
    return WordMapper(nlp, config_file, half_space_char)


# -----------------------------------------------------------
class SpellCheker:
    def __init__(self, nlp: Language):
        self.spell = SpellCheck()

    def __call__(self, doc):
        return self.spell.spell_corrector(doc)


@Language.factory("spell_checker", default_config={})
def spell_checker(nlp: Language, name: str):
    return SpellCheker(nlp)


# -----------------------------------------------------------
nlp = spacy.blank("fa")

conf_path = os.path.dirname(os.path.realpath(__file__)) + "/config/"

nlp.tokenizer = WhitespaceTokenizer(nlp)
nlp.add_pipe("char_normalizer", first=True,
             config={"config_file": conf_path + 'character_mappings.json'})
nlp.add_pipe("spell_checker", after="char_normalizer", config={})
nlp.add_pipe("date2str", after="spell_checker", config={})
nlp.add_pipe("time2str", after="date2str", config={})
nlp.add_pipe("num2str", after="time2str", config={})
nlp.add_pipe("abbreviation2word", after="num2str", config={})
nlp.add_pipe("affix2norm", after="abbreviation2word",
             config={"config_file": conf_path + 'affix.json', "double_postfix_joint": True})
nlp.add_pipe("word_mapper", after="affix2norm",
             config={"config_file": conf_path + 'word_mappings.json', "half_space_char": "  "})

nlp.add_pipe("punctuation_remover", after="abbreviation2word", config={})
nlp.add_pipe("word_level_tokenizer")

nlp_blank = spacy.blank("fa")
nlp_blank.tokenizer = WhitespaceTokenizer(nlp_blank)
