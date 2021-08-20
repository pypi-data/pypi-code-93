import typing as tp
import re

from weak_postagger.logic.param import SET_WORDS, PREPOSITION_ARTICLES, \
    OBLIQUE_PERSONAL_PRONOUN, VERB_EXCEPTIONS, ADDRESS


class RuleBasedDisambiguation:
    """
        Class responsible for disambiguate POS Tag labels of a sentence.
        The disambiguation is done using rules created by the patterns observed on portuguese syntax.
        
        Methods:
        --------
        * label_disambiguation : Analyses the labels for a sentence and decides on a single valid label for
        the ambiguous or missing labels.
        
    """
    
    def __init__(self):
        """ Initializes the class with the default words and ambiguity cases. """
        self.__preposition_article = PREPOSITION_ARTICLES
        self.__oblique_personal_pronoun = OBLIQUE_PERSONAL_PRONOUN
        self.__verb_exceptions = VERB_EXCEPTIONS
        self.__address = ADDRESS
        self.__set_words = SET_WORDS
        
        self.__ambiguity_methods_dict = {
            "['SUBS', 'VERB']": self.__case_verb_substantive,
            "['PREP', 'VERB']": self.__case_verb_preposition,
            "['ADJ', 'SUBS']": self.__case_adjective_substantive,
            "['ADJ', 'VERB']": self.__case_verb_adjective,
            "['INT', 'SUBS']": self.__case_interjection_substantive,
            "['PRON', 'VERB']": self.__case_pronoun_verb,
            "['ADV', 'INT']": self.__case_adverb_interjection,
            "['ADV', 'PRON']": self.__case_adverb_pronoun,
            "['ADJ', 'ADV']": self.__case_adverb_adjective,
            
        }
    
    def label_disambiguation(self, sentence: str, labels: str) -> tp.Tuple[str, str]:
        """
            Analyses the labels for a sentence and decides on a single valid label for the ambiguous or missing labels.
        
            A missing label appears as `['ABSTAIN']` and an ambiguous label appears in the format: `['VERB|ART']`
            
        :param sentence: Sentence being labeled.
        :type sentence: `str`
        :param labels: List of POS Tag labels for that sentence.
        :type labels: `str`
        :return: A tuple with the preprocessed sentence and the labels for the words on the sentence.
        :rtype: `tp.Tuple[str, str]`
        """
        labels = [label.split('|') if '|' in label else [label] for label in labels.split()]
        corrected_labels = labels.copy()
        
        for index, label in enumerate(labels):
            if len(label) > 1:
                corrected_labels = self.__correct_label(sentence.split(), corrected_labels, index)
        
        resulting_labels = ' '.join(
            ['|'.join([label for label in word_labels]) if len(word_labels) > 1 else word_labels[0]
             for word_labels in corrected_labels]
            )
        
        return sentence, resulting_labels
    
    def __is_main_verb(self, word: str) -> bool:
        """
            Checks if a word is a main verb on a sentence.

        :param word: Word to be analysed.
        :type word: `str`
        :return: Flags if the word is a main verb.
        :rtype: `str`
        """
        if len(re.findall('ido$', word)) > 0 or \
                len(re.findall('ado$', word)) > 0 or \
                len(re.findall('ndo$', word)) > 0 or \
                len(re.findall('r$', word)) > 0 or \
                word in self.__verb_exceptions:
            return True
        else:
            return False
    
    @staticmethod
    def __has_auxiliary_verb_structure(labels: tp.List[tp.List[str]], word_index: int) -> bool:
        """
            Checks if a word can be part of an auxiliary verb in a sentence structure.

        :param labels: Sentence's labels.
        :type labels: `tp.List[tp.List[str]]`
        :param word_index: Index on the sentence of the word being analysed.
        :type word_index: `int`
        :return: Flags if the word can be in an auxiliary verb structure or not.
        :rtype: `bool`
        """
        if word_index < len(labels) - 1 and labels[word_index + 1] in [['VERB'], ['PART']]:
            return True
        else:
            return False
    
    def __auxiliary_verb_or_alt_decision(self, sentence: tp.List[str], word_index: int,
                                         alt_label: tp.List[str], steps_forward: int = 0) -> tp.List[str]:
        """
            Decides between labeling a word an auxiliary verb or an alternative given label.

        :param sentence: Sentence being labeled.
        :type sentence: `str`
        :param word_index: Index on the sentence of the word being analysed.
        :type word_index: `int`
        :param steps_forward: How many steps back is the word being checked. Defaults to zero.
        :type steps_forward: `int`
        :return: Label decided for the word.
        :rtype: `tp.List[str]`
        """
        if word_index < len(sentence) - steps_forward and self.__is_main_verb(sentence[word_index + steps_forward]):
            return ['VERB']
        else:
            return alt_label
    
    @staticmethod
    def __check_label_after(labels: tp.List[tp.List[str]], word_index: int,
                            target_label: tp.List[str], steps_forward: int = 1) -> bool:
        """
            Checks if the word after the one on the `word_index` is of label `target_label`.

        :param labels: Sentence's labels.
        :type labels: `tp.List[tp.List[str]]`
        :param word_index: Index on the sentence of the word being analysed.
        :type word_index: `int`
        :param target_label: Label being checked.
        :type target_label: `tp.List[str]`
        :param steps_forward: How many steps back is the word being checked. Defaults to one.
        :type steps_forward: `int`
        :return: Flags if the word is an auxiliary verb or not.
        :rtype: `bool`
        """
        if word_index < len(labels) - steps_forward and any([label in target_label
                                                             for label in labels[word_index + steps_forward]]):
            return True
        else:
            return False
    
    @staticmethod
    def __check_label_before(labels: tp.List[tp.List[str]], word_index: int,
                             target_label: tp.List[str], steps_back: int = 1) -> bool:
        """
            Checks if the last word before the one on the `word_index` is of label `target_label`.

        :param labels: Sentence's labels.
        :type labels: `tp.List[tp.List[str]]`
        :param word_index: Index on the sentence of the word being analysed.
        :type word_index: `int`
        :param target_label: Label being checked.
        :type target_label: `tp.List[str]`
        :param steps_back: How many steps back is the word being checked. Defaults to one.
        :type steps_back: `int`
        :return: Flags if the word is an auxiliary verb or not.
        :rtype: `bool`
        """
        if (word_index - steps_back >= 0) and any([label in target_label for label in labels[word_index - steps_back]]):
            return True
        else:
            return False
    
    @staticmethod
    def __check_word_before(sentence: tp.List[str], word_index: int,
                            target_words: tp.List[str], steps_back: int = 1) -> bool:
        """
            Checks if the last word before the one on the `word_index` is one of the `target_words`.

        :param sentence: Sentence's labels.
        :type sentence: `tp.List[str]`
        :param word_index: Index on the sentence of the word being analysed.
        :type word_index: `int`
        :param target_words: Words being checked.
        :type target_words: `tp.List[str]`
        :param steps_back: How many steps back is the word being checked. Defaults to one.
        :type steps_back: `int`
        :return: Flags if the word is an auxiliary verb or not.
        :rtype: `bool`
        """
        if (word_index - steps_back >= 0) and (sentence[word_index - steps_back] in target_words):
            return True
        else:
            return False
    
    def __correct_label(self, sentence: tp.List[str],
                        labels: tp.List[tp.List[str]], index: int) -> tp.List[tp.List[str]]:
        """
            Checks which case of ambiguity the label falls into and directs to the appropriated correction.
            
        :param sentence: Text being labeled.
        :type sentence: `tp.List[str]`
        :param labels: Current label for the sentence:
        :type labels: `tp.List[tp.List[str]]`
        :param index: Word being analysed.
        :type index: `int`
        :return: Corrected labels for the sentence.
        :rtype: `tp.List[tp.List[str]]`
        """
        if sentence[index] in self.__set_words:
            labels[index] = self.__set_words[sentence[index]]
        elif str(labels[index]) in self.__ambiguity_methods_dict:
            labels = self.__check_for_ambiguity(sentence, labels, index)
        
        elif sentence[index] == 'como':
            if index == 0:
                labels[index] = ['ADV']
            elif self.__check_label_after(labels, index, ['SUBS']):
                labels[index] = ['PREP']
            elif self.__check_label_after(labels, index, ['VERB']):
                labels[index] = ['ADV']
        
        elif sentence[index] == 'bom':
            if labels[index - 1] == ['INT'] or index == 0:
                labels[index] = ['INT']
        
        elif sentence[index] == 'tarde':
            if self.__check_label_before(labels, index, ['INT']):
                labels[index] = ['SUBS']
        
        elif sentence[index] == 'para':
            if self.__check_label_after(labels, index, ['VERB']):
                labels[index] = ['ADV']
            else:
                labels[index] = ['PREP']
        
        return labels
    
    def __check_for_ambiguity(self, sentence: tp.List[str],
                              labels: tp.List[tp.List[str]], index: int) -> tp.List[tp.List[str]]:
        """
            Applies the disambiguation rules from `self.__ambiguity_methods_dict`.
            
        :param sentence: Text being labeled.
        :type sentence: `tp.List[str]`
        :param labels: Current label for the sentence:
        :type labels: `tp.List[tp.List[str]]`
        :param index: Word being analysed.
        :type index: `int`
        :return: Corrected labels for the sentence.
        :rtype: `tp.List[tp.List[str]]`
        """
        ambiguous_label = str(labels[index])
        apply_disambiguation_method = self.__ambiguity_methods_dict.get(ambiguous_label, '')
        
        if apply_disambiguation_method:
            labels = apply_disambiguation_method(sentence, labels, index)
        elif ambiguous_label == "['ART', 'SUBS']":
            labels[index] = ['ART']
        elif ambiguous_label == "['ADV', 'PREP']":
            if index - 1 >= 0 and str(labels[index - 1]) == "['PREP']":
                labels[index] = ['ADV']
        
        return labels
    
    def __case_verb_substantive(self, sentence: tp.List[str],
                                labels: tp.List[tp.List[str]], word_index: int) -> tp.List[tp.List[str]]:
        """
            Corrects ambiguities between verbs and substantives.
            
        :param sentence: Text being labeled.
        :type sentence: `tp.List[str]`
        :param labels: Current label for the sentence:
        :type labels: `tp.List[tp.List[str]]`
        :param word_index: Word being analysed.
        :type word_index: `int`
        :return: Corrected labels for the sentence.
        :rtype: `tp.List[tp.List[str]]`
        """
        if self.__has_auxiliary_verb_structure(labels, word_index):
            labels[word_index] = self.__auxiliary_verb_or_alt_decision(sentence, word_index, ['SUBS'], steps_forward=1)
        
        elif word_index != 0:
            if self.__check_label_before(labels, word_index, ['PREP']):
                if self.__check_word_before(sentence, word_index, self.__preposition_article):
                    labels[word_index] = ['SUBS']
                elif self.__check_label_before(labels, word_index, ['VERB'], steps_back=2):
                    labels[word_index] = self.__auxiliary_verb_or_alt_decision(sentence, word_index, ['SUBS'])
                elif self.__check_label_before(labels, word_index, ['SUBS'], steps_back=2):
                    labels[word_index] = ['SUBS']
            
            elif self.__check_label_before(labels, word_index, ['VERB']):
                labels[word_index] = self.__auxiliary_verb_or_alt_decision(sentence, word_index, ['SUBS'])
            
            elif self.__check_label_before(labels, word_index, ['PRON']):
                if self.__check_word_before(sentence, word_index, self.__oblique_personal_pronoun):
                    labels[word_index] = ['VERB']
                else:
                    labels[word_index] = ['SUBS']
            
            elif self.__check_label_before(labels, word_index, ['SUBS', 'NUM', 'ART']):
                labels[word_index] = ['SUBS']
        
        return labels
    
    def __case_verb_preposition(self, sentence, labels, word_index) -> tp.List[tp.List[str]]:
        """
            Corrects ambiguities between verbs and prepositions.

        :param sentence: Text being labeled.
        :type sentence: `tp.List[str]`
        :param labels: Current label for the sentence:
        :type labels: `tp.List[tp.List[str]]`
        :param word_index: Word being analysed.
        :type word_index: `int`
        :return: Corrected labels for the sentence.
        :rtype: `tp.List[tp.List[str]]`
        """
        if self.__has_auxiliary_verb_structure(labels, word_index):
            labels[word_index] = self.__auxiliary_verb_or_alt_decision(sentence, word_index, ['PREP'], steps_forward=1)
        elif word_index != 0:
            if sentence[word_index] == 'sobre':
                labels[word_index] = ['PREP']
            
            elif sentence[word_index] == 'visto':
                if self.__check_label_before(labels, word_index, ['VERB']):
                    labels[word_index] = ['VERB']
                else:
                    labels[word_index] = ['PREP']
            
            elif sentence[word_index] == 'entre':
                if self.__check_word_before(sentence, word_index, ['que'], steps_back=2) and \
                        self.__check_word_before(sentence, word_index, ['eu']):
                    labels[word_index] = ['VERB']
                else:
                    labels[word_index] = ['PREP']
        
        return labels
    
    def __case_pronoun_verb(self, sentence, labels, word_index) -> tp.List[tp.List[str]]:
        """
            Corrects ambiguities between verbs and pronouns.

        :param sentence: Text being labeled.
        :type sentence: `tp.List[str]`
        :param labels: Current label for the sentence:
        :type labels: `tp.List[tp.List[str]]`
        :param word_index: Word being analysed.
        :type word_index: `int`
        :return: Corrected labels for the sentence.
        :rtype: `tp.List[tp.List[str]]`
        """
        if self.__has_auxiliary_verb_structure(labels, word_index):
            labels[word_index] = self.__auxiliary_verb_or_alt_decision(sentence, word_index, ['PRON'], steps_forward=1)
        elif word_index != 0:
            
            if self.__check_label_before(labels, word_index, ['VERB']):
                labels[word_index] = self.__auxiliary_verb_or_alt_decision(sentence, word_index, ['PRON'])
        
        return labels
    
    def __case_verb_adjective(self, sentence, labels, word_index) -> tp.List[tp.List[str]]:
        """
            Corrects ambiguities between verbs and adjectives.

        :param sentence: Text being labeled.
        :type sentence: `tp.List[str]`
        :param labels: Current label for the sentence:
        :type labels: `tp.List[tp.List[str]]`
        :param word_index: Word being analysed.
        :type word_index: `int`
        :return: Corrected labels for the sentence.
        :rtype: `tp.List[tp.List[str]]`
        """
        if self.__has_auxiliary_verb_structure(labels, word_index):
            labels[word_index] = self.__auxiliary_verb_or_alt_decision(sentence, word_index, ['ADJ'], steps_forward=1)
        elif word_index == 0:
            labels[word_index] = ['VERB']
        else:
            if self.__check_label_before(labels, word_index, ['VERB']):
                labels[word_index] = self.__auxiliary_verb_or_alt_decision(sentence, word_index, ['ADJ'],
                                                                           steps_forward=1)
            elif self.__check_label_before(labels, word_index, ['SUBS']):
                labels[word_index] = ['VERB']
            
            elif self.__check_label_before(labels, word_index, ['PRON']):
                if self.__check_label_before(labels, word_index, self.__oblique_personal_pronoun):
                    labels[word_index] = ['VERB']
                else:
                    labels[word_index] = ['ADJ']
        
        return labels
    
    def __case_adverb_adjective(self, sentence, labels, word_index) -> tp.List[tp.List[str]]:
        """
            Corrects ambiguities between adverbs and adjectives.

        :param sentence: Text being labeled.
        :type sentence: `tp.List[str]`
        :param labels: Current label for the sentence:
        :type labels: `tp.List[tp.List[str]]`
        :param word_index: Word being analysed.
        :type word_index: `int`
        :return: Corrected labels for the sentence.
        :rtype: `tp.List[tp.List[str]]`
        """
        if word_index == 0:
            labels[word_index] = ['ADV']
        
        elif self.__check_label_before(labels, word_index, ['VERB']):
            labels[word_index] = ['ADV']
        
        return labels
    
    def __case_adjective_substantive(self, sentence, labels, word_index) -> tp.List[tp.List[str]]:
        """
            Corrects ambiguities between adjectives and substantives.

        :param sentence: Text being labeled.
        :type sentence: `tp.List[str]`
        :param labels: Current label for the sentence:
        :type labels: `tp.List[tp.List[str]]`
        :param word_index: Word being analysed.
        :type word_index: `int`
        :return: Corrected labels for the sentence.
        :rtype: `tp.List[tp.List[str]]`
        """
        if word_index != 0:
            if self.__check_label_before(labels, word_index, ['ART', 'PRON', 'VERB', 'NUM']):
                labels[word_index] = ['SUBS']
            
            elif self.__check_label_before(labels, word_index, ['PREP']):
                if self.__check_label_before(labels, word_index, ['SUBS'], steps_back=2):
                    labels[word_index] = ['SUBS']
            
            elif sentence[word_index] in ['plano', 'planos', 'acordo', 'seguro', 'celular']:
                labels[word_index] = ['SUBS']
            
            elif sentence[word_index] in ['novo']:
                labels[word_index] = ['ADJ']
        
        return labels
    
    def __case_interjection_substantive(self, sentence, labels, word_index) -> tp.List[tp.List[str]]:
        """
            Corrects ambiguities between interjections and substantives.

        :param sentence: Text being labeled.
        :type sentence: `tp.List[str]`
        :param labels: Current label for the sentence:
        :type labels: `tp.List[tp.List[str]]`
        :param word_index: Word being analysed.
        :type word_index: `int`
        :return: Corrected labels for the sentence.
        :rtype: `tp.List[tp.List[str]]`
        """
        if word_index == 0:
            labels[word_index] = ['INT']
        else:
            if self.__check_label_before(labels, word_index, ['PREP']):
                if self.__check_label_before(labels, word_index, ['SUBS'], steps_back=2):
                    labels[word_index] = ['SUBS']
            elif self.__check_label_before(labels, word_index, ['INT']):
                labels[word_index] = ['INT']
        return labels
    
    def __case_adverb_interjection(self, sentence, labels, word_index) -> tp.List[tp.List[str]]:
        """
            Corrects ambiguities between interjections and adverbs.

        :param sentence: Text being labeled.
        :type sentence: `tp.List[str]`
        :param labels: Current label for the sentence:
        :type labels: `tp.List[tp.List[str]]`
        :param word_index: Word being analysed.
        :type word_index: `int`
        :return: Corrected labels for the sentence.
        :rtype: `tp.List[tp.List[str]]`
        """
        if word_index != 0:
            if self.__check_label_before(labels, word_index, ['VERB', 'PREP', 'SUBS']):
                labels[word_index] = ['ADV']
        return labels
    
    def __case_adverb_pronoun(self, sentence, labels, word_index) -> tp.List[tp.List[str]]:
        """
            Corrects ambiguities between adverbs and pronouns.

        :param sentence: Text being labeled.
        :type sentence: `tp.List[str]`
        :param labels: Current label for the sentence:
        :type labels: `tp.List[tp.List[str]]`
        :param word_index: Word being analysed.
        :type word_index: `int`
        :return: Corrected labels for the sentence.
        :rtype: `tp.List[tp.List[str]]`
        """
        if word_index == 0:
            if self.__check_label_after(labels, word_index, ['VERB']):
                labels[word_index] = ['PRON']
        elif self.__check_label_before(labels, word_index, ['VERB']):
            labels[word_index] = ['ADV']
        return labels
