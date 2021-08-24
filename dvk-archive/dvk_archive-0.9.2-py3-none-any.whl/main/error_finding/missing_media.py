#!/usr/bin/env python3

from argparse import ArgumentParser
from dvk_archive.main.file.dvk import Dvk
from dvk_archive.main.file.dvk_handler import DvkHandler
from dvk_archive.main.processing.string_processing import truncate_path
from os import getcwd
from os.path import abspath, exists, isdir
from tqdm import tqdm
from typing import List

def get_missing_media_dvks(directory:str=None) -> List[str]:
    """
    Returns list of Dvks missing their associated media file(s).

    :param directory: Directory in which to search, defaults to None
    :type directory: str, optional
    :return: Dvk files with missing primary or secondary media
    :rtype: list[str]
    """
    # RETURN EMPTY LIST IF DIRECTORY IS INVALID
    if directory is None or not exists(directory) or not isdir(directory):
        return []
    # READ DVKS FOR THE GIVEN DIRECTORY
    dvk_handler = DvkHandler()
    dvk_handler.read_dvks(directory)
    dvk_handler.sort_dvks("a")
    # CHECK EACH DVK TO SEE IF LINKED MEDIA EXISTS
    missing = []
    size = dvk_handler.get_size()
    print("Finding DVKs with missing media:")
    for dvk_num in tqdm(range(0, size)):
        dvk = dvk_handler.get_dvk(dvk_num)
        media = dvk.get_media_file()
        secondary = dvk.get_secondary_file()
        # ADD TO MISSING LIST IF MEDIA DOESN'T EXIST
        if (media is None
                or not exists(media)
                or (secondary is not None and not exists(secondary))):
            missing.append(dvk.get_dvk_file())
    # RETURN LIST OF DVKS WITH MISSING MEDIA
    return missing

def main():
    """
    Sets up commands for getting DVKs with missing media.
    """
    parser = ArgumentParser()
    parser.add_argument(
            "directory",
            help="Directory in which to search for DVKs with missing linked media.",
            nargs="?",
            type=str,
            default=str(getcwd()))
    args = parser.parse_args()
    full_directory = abspath(args.directory)
    # CHECK IF DIRECTORY EXISTS
    if (full_directory is not None
            and exists(full_directory)
            and isdir(full_directory)):
        # GET LIST OF DVKS WITH MISSING MEDIA
        missing = get_missing_media_dvks(full_directory)
        # PRINT LIST
        if len(missing) > 0:
            for item in missing:
                print(truncate_path(full_directory, item))
        else:
            print("\033[32mNo DVKs with missing media found.\033[0m")
    else:
        print("Invalid directory")

if __name__ == "__main__":
    main()
