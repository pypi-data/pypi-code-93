#!/usr/bin/env python3

from argparse import ArgumentParser
from dvk_archive.main.file.dvk import Dvk
from dvk_archive.main.file.dvk_handler import DvkHandler
from dvk_archive.main.processing.html_processing import clean_element
from os import getcwd
from os.path import abspath, exists, isdir
from tqdm import tqdm

def reformat_dvks(dvk_handler:DvkHandler=None):
    """
    Reformats DVKs to fit the current formatting standard.

    :param dvk_handler: Contains Dvks to be formatted, defaults to None
    :type dvk_handler: DvkHandler, optional
    """
    # TEST IF DVK HANDLER IS VALID
    if dvk_handler is not None:
        # REFORMAT EACH FILE
        print("Reformatting DVK Files:")
        size = dvk_handler.get_size()
        for dvk_num in tqdm(range(0, size)):
            dvk = dvk_handler.get_dvk(dvk_num)
            # CLEAN UP HTML IN DVK DESCRIPTIONS
            desc = dvk.get_description()
            if desc is not None:
                desc = clean_element(desc, False)
                dvk.set_description(desc)
            # WRITE DVK
            dvk.write_dvk()
            # UPDATE EXTENSIONS
            dvk.update_extensions()

def reformat_directory(directory:str=None):
    """
    Reformats DVKs in a given directory.

    :param directory: Directory in which to reformat DVKs, defaults to None
    :type directory: str, optional
    """
    # CHECK IF DIRECTORY EXISTS
    if directory is not None and exists(directory) and isdir(directory):
        # READ DVKS IN THE GIVEN DIRECTORY
        dvk_handler = DvkHandler()
        dvk_handler.read_dvks(directory)
        # REFORMAT DVKS
        reformat_dvks(dvk_handler)
    else:
        print("Invalid directory")

def main():
    """
    Sets up reformatting DVK files.
    """
    parser = ArgumentParser()
    parser.add_argument(
        "directory",
        help="Directory in which to reformat DVKs.",
        nargs="?",
        type=str,
        default=str(getcwd()))
    args = parser.parse_args()
    reformat_directory(abspath(args.directory))

if __name__ == "__main__":
    main()
