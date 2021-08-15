#!/usr/bin/env python3

"""
This Python script is designed to query internal repositories for the
homophones associated with the given word.
"""
__author__ = 'John Bumgarner'
__date__ = 'June 11, 2021'
__status__ = 'Production'
__license__ = 'MIT'
__copyright__ = "Copyright (C) 2021 John Bumgarner"

##################################################################################
# Date Completed: June 11, 2021
# Author: John Bumgarner
#
# Date Last Revised: July 4, 2021
# Revised by: John Bumgarner
##################################################################################

##################################################################################
# “AS-IS” Clause
#
# Except as represented in this agreement, all work produced by Developer is
# provided “AS IS”. Other than as provided in this agreement, Developer makes no
# other warranties, express or implied, and hereby disclaims all implied warranties,
# including any warranty of merchantability and warranty of fitness for a particular
# purpose.
##################################################################################

##################################################################################
# Python imports required for basic operations
##################################################################################
import os
import sys
import pickle
import logging
import traceback
from wordhoard.utilities import word_verification

logger = logging.getLogger(__name__)

PARENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

# Opening the pickle file that contains a nested list of common
# English language homophones.
try:
    _file_known_homophones = os.path.join(PARENT_DIRECTORY, 'files/common_english_homophones.pkl')
    with open(_file_known_homophones, 'rb') as _eng_homophones:
        _known_homophones_list = pickle.load(_eng_homophones)
        _eng_homophones.close()
except FileNotFoundError as error:
    logger.error('The common_english_homophones.pkl file was not found. Aborting operation.')
    logger.error(''.join(traceback.format_tb(error.__traceback__)))
    sys.exit(1)
except OSError as error:
    logger.error(f"An OS error occurred when trying to open the file common_english_homophones.pkl")
    logger.error(''.join(traceback.format_tb(error.__traceback__)))
    sys.exit(1)


# Opening the pickle file that contains a nested list of English
# language words that have no known homophones.
try:
    _file_no_known_homophones = os.path.join(PARENT_DIRECTORY, 'files/no_homophones_english.pkl')
    with open(_file_no_known_homophones, 'rb') as _no_eng_homophones:
        _no_homophones_list = pickle.load(_no_eng_homophones)
        _no_eng_homophones.close()
except FileNotFoundError as error:
    logger.error('The no_homophones_english.pkl file was not found. Aborting operation.')
    logger.error(''.join(traceback.format_tb(error.__traceback__)))
    sys.exit(1)
except OSError as error:
    logger.error(f"An OS error occurred when trying to open the file no_homophones_english.pkl")
    logger.error(''.join(traceback.format_tb(error.__traceback__)))
    sys.exit(1)


class Homophones(object):
    """
    This class is used to query internal files containing
    English language homophones associated with a specific word.

    Usage: homophone = Homophones(word)
           results = homophone.find_homophones()
    """

    def __init__(self, word):
        """
        :param word: string containing the variable to search for
        """
        self._word = word

    def _validate_word(self):
        """
        This function is designed to validate that the syntax for
        a string variable is in an acceptable format.

        :return: True or False
        :rtype: boolean
        """
        valid_word = word_verification.validate_word_syntax(self._word)
        if valid_word:
            return valid_word
        else:
            logger.error(f'The word {self._word} was not in a valid format.')
            logger.error(f'Please verify that the word {self._word} is spelled correctly.')

    def _common_english_homophones(self):
        """
        This function iterates through a list of known
        English language homophones.

        :return:
            homophones: list of homophones

        :rtype: list
        """
        global _known_homophones_list
        rtn_list = []
        for homophones in _known_homophones_list:
            match = bool([word for word in homophones if word == self._word])
            if match:
                for word in homophones:
                    if word != self._word:
                        rtn_list.append(f'{self._word} is a homophone of {word}')
        if len(rtn_list) > 0:
            return list(set(rtn_list))

    def _english_words_without_homophones(self):
        """
        This function iterates through a list of English
        language words with no known homophones.

        :return: no homophones for word
        :rtype: str
        """
        global _no_homophones_list
        match = bool(self._word in _no_homophones_list)
        if match:
            return f'no homophones for {self._word}'

    def find_homophones(self):
        """
        This function queries multiple lists to find an
        English language homophones associated with the
        specific word provided to the Class Homophones.

        :return:
            homophones: list of homophones
            no_homophones: string

        :rtype: list
        :rtype: str
        """
        valid_word = self._validate_word()
        if valid_word:
            known_english_homophones = self._common_english_homophones()
            if known_english_homophones:
                return known_english_homophones
            elif not known_english_homophones:
                return self._english_words_without_homophones()
