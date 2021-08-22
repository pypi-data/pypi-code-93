# !/usr/bin/env python
# coding=utf-8

"""
Allows user to add to a custom dictionary using the command line.
This script assumes that the format is to have one word per line, and nothing else on the line.
"""
import argparse
import logging
import sys
from common_wrangler.common import (GOOD_RET, INPUT_ERROR, warning, file_rows_to_list, IO_ERROR, list_to_file)

__author__ = 'hmayes'

# logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants #

# Defaults #
DEF_DICT_LOC = '/Users/hmayes/Dropbox/NREL/code/hmayes_cust.dic'

# Logic #


# CLI Processing #


def parse_cmdline(argv):
    """
    Returns the parsed argument list and return code.
    :param argv: is a list of arguments, or `None` for ``sys.argv[1:]``.
    """
    if argv is None:
        argv = sys.argv[1:]

    # initialize the parser object:
    parser = argparse.ArgumentParser(description='Adds words to a custom dictionary in the format of a simple '
                                                 'text file with one word per line, and nothing else on each line.')
    parser.add_argument("word", help="The word to be added to the dictionary. The script will ensure that the word "
                                     "appears only once in the dictionary file, and is inserted in alphabetical order.")
    parser.add_argument("-d", "--dict_loc", help="The location of the dictionary file to which a word is to be added. "
                                                 "The default location is: ".format(DEF_DICT_LOC),
                        default=DEF_DICT_LOC)

    args = None
    try:
        args = parser.parse_known_args(argv)
    except SystemExit as e:
        if hasattr(e, 'code') and e.code == 0:
            return args, GOOD_RET
        warning(e)
        parser.print_help()
        return args, INPUT_ERROR

    return args, GOOD_RET


def main(argv=None):
    """ Runs the main program.

    :param argv: The command line arguments.
    :return: The return code for the program's termination.
    """
    args, ret = parse_cmdline(argv)
    if ret != GOOD_RET or args is None:
        return ret

    try:
        # set prevents duplicates
        dict_set = set(file_rows_to_list(args[0].dict_loc))
        for input_word in [args[0].word] + args[1]:
            # keep consistency of lower-case words only
            word_to_add = input_word.lower()
            dict_set.add(word_to_add)
        # convert set to list to sort and write to file
        dict_list = list(dict_set)
        dict_list.sort()
        list_to_file(dict_list, args[0].dict_loc)
    except IOError as e:
        warning("Problems reading file: {}".format(e))
        return IO_ERROR

    return GOOD_RET  # success


if __name__ == '__main__':
    status = main()
    sys.exit(status)
