#!/usr/bin/env python3

from argparse import ArgumentParser
from dvk_archive.main.file.dvk import Dvk
from dvk_archive.main.file.dvk_handler import DvkHandler
from dvk_archive.main.file.dvk_handler import get_directories
from dvk_archive.main.processing.string_processing import truncate_path
from os import getcwd, listdir
from os.path import abspath, exists, isdir, join
from tqdm import tqdm
from typing import List

def get_unlinked_media(directory:str=None) -> List[str]:
    """
    Returns a list of files not linked to a DVK file.
    Only returns files in the same directories as DVK files.

    :param directory: Directory in which to search, defaults to None
    :type directory: str, optional
    :return: List of unlinked files
    :rtype: list[str]
    """
    # RETURN EMPTY LIST IF DIRECTORY IS INVALID
    if directory is None or not exists(directory) or not isdir(directory):
        return []
    # READ DVKS IN DIRECTORY
    dvk_handler = DvkHandler()
    dvk_handler.read_dvks(directory)
    # GET LIST OF DIRECTORIES WITH DVK FILES
    dirs = sorted(get_directories(directory))
    # RUN THROUGH DIRECTORIES
    unlinked = []
    print("Finding unlinked media files:")
    for path in tqdm(dirs):
        files = sorted(listdir(abspath(path)))
        # RUN THROUGH ALL FILES IN THE DIRECTORY
        for file in files:
            # ADD TO UNLINKED IF NO DVKS LINK THIS FILE
            full_file = abspath(join(path, file))
            if (not file.endswith(".dvk")
                    and not isdir(full_file)
                    and not dvk_handler.contains_media_file(full_file)):
                unlinked.append(abspath(full_file))
    return unlinked

def main():
    """
    Sets up commands for getting files with no corresponding DVKs
    """
    parser = ArgumentParser()
    parser.add_argument(
            "directory",
            help="Directory in which to search for unlinked media.",
            nargs="?",
            type=str,
            default=str(getcwd()))
    args = parser.parse_args()
    full_directory = abspath(args.directory)
    # CHECK IF DIRECTORY EXISTS
    if (full_directory is not None
            and exists(full_directory)
            and isdir(full_directory)):
        # GET LIST OF UNLINKED MEDIA FILES
        unlinked = get_unlinked_media(full_directory)
        # PRINT LIST
        if len(unlinked) > 0:
            for item in unlinked:
                print(truncate_path(full_directory, item))
        else:
            print("\033[32mNo unlinked media files found.\033[0m")
    else:
        print("Invalid directory")

if __name__ == "__main__":
    main()
