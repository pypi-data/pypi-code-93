# !/usr/bin/env python
# coding=utf-8

"""
Renames files which have spaces in their names
"""
import argparse
import logging
import os
import sys
import re
from common_wrangler.common import (GOOD_RET, INPUT_ERROR, warning)

__author__ = 'hmayes'

# logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants #

# Defaults #

# want any files with a space in the name
DEF_FILE_PAT = ' '
DEF_NEW_FILE_PAT = ''

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
    parser = argparse.ArgumentParser(description='Renames files which contain (by default) a space in the name to '
                                                 'the same filename without the space. The pattern can be changed '
                                                 'to replace a different character or pattern')
    parser.add_argument("-d", "--base_dir", help="The starting point for a file search "
                                                 "(defaults to current directory)",
                        default=os.getcwd())
    parser.add_argument("-l", "--lowercase", help="Flag to specify that files should be renamed to be all in "
                                                  "lowercase.",
                        action='store_true')
    parser.add_argument('-n', "--new_pattern", help="The new pattern to use in changing the file name "
                                                    "(defaults to '{}')".format(DEF_NEW_FILE_PAT),
                        default=DEF_NEW_FILE_PAT)
    parser.add_argument("-o", "--only_dir", help="Flag to specify that only the directory specified with '-d' "
                                                 "(which defaults to current directory) is to be searched.",
                        action='store_true')
    parser.add_argument('-p', "--pattern", help="The file pattern to search for "
                                                "(defaults to '{}')".format(DEF_FILE_PAT),
                        default=DEF_FILE_PAT)
    parser.add_argument("-t", "--test_mode", help="Flag to list files that would be renamed, without renaming them.",
                        action='store_true')

    args = None
    try:
        args = parser.parse_args(argv)
    except SystemExit as e:
        if hasattr(e, 'code') and e.code == 0:
            return args, GOOD_RET
        warning(e)
        parser.print_help()
        return args, INPUT_ERROR

    return args, GOOD_RET


def rename_file(tgt_dir, fname, pattern, new_pattern, make_lowercase, test_flag):
    old_name = os.path.abspath(os.path.join(tgt_dir, fname))
    if make_lowercase:
        new_base = fname.lower()
    else:
        new_base = fname.replace(pattern, new_pattern)
    new_name = os.path.abspath(os.path.join(tgt_dir, new_base))

    rel_old_name = os.path.relpath(old_name)
    rel_new_name = os.path.relpath(new_name)

    if test_flag:
        print("Would rename {} --> {}".format(rel_old_name, rel_new_name))
    else:
        os.rename(old_name, new_name)
        print("Renamed {} --> {}".format(rel_old_name, rel_new_name))


def rename_files_by_dir(tgt_dir, pattern, new_pattern, no_subdir, make_lowercase, test_flag):
    """
    Alternate filename matching
    :param tgt_dir: base file in which to search
    :param pattern: string to replaced
    :param new_pattern: string to replace the pattern string
    :param no_subdir: boolean to indicate if only the current directory should be searched
    :param make_lowercase: boolean to indicate if file names should be converted to lowercase
    :param test_flag: boolean to indicate if files to rename should be listed without renaming
    :return: an integer representing the number of files renamed
    """
    num_files_renamed = 0
    if make_lowercase:
        pat_match = re.compile(r".*[A-Z].*")
    else:
        pat_match = re.compile(r".*" + re.escape(pattern) + r".*")
    if no_subdir:
        file_list = os.listdir(tgt_dir)
        for fname in file_list:
            if pat_match.match(fname):
                rename_file(tgt_dir, fname, pattern, new_pattern, make_lowercase, test_flag)
                num_files_renamed += 1
    else:
        for root, dirs, files in os.walk(tgt_dir):
            for fname in files:
                if pat_match.match(fname):
                    rename_file(root, fname, pattern, new_pattern, make_lowercase, test_flag)
                    num_files_renamed += 1
    return num_files_renamed


def main(argv=None):
    """ Runs the main program.

    :param argv: The command line arguments.
    :return: The return code for the program's termination.
    """
    args, ret = parse_cmdline(argv)
    if ret != GOOD_RET or args is None:
        return ret

    num_renamed_files = rename_files_by_dir(args.base_dir, args.pattern, args.new_pattern, args.only_dir,
                                            args.lowercase, args.test_mode)
    if args.test_mode:
        print("Ran rename_files in testing mode; no files have been renamed\n"
              "If not in testing mode, would rename {} files".format(num_renamed_files))
    else:
        print("Found and renamed {} files".format(num_renamed_files))
    return GOOD_RET  # success


if __name__ == '__main__':
    status = main()
    sys.exit(status)
