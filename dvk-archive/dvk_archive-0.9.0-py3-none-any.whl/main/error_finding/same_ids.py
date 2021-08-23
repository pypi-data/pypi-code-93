#!/usr/bin/env python3

from argparse import ArgumentParser
from dvk_archive.main.file.dvk import Dvk
from dvk_archive.main.file.dvk_handler import DvkHandler
from dvk_archive.main.processing.string_processing import truncate_path
from os import getcwd
from os.path import abspath, exists, isdir
from tqdm import tqdm
from typing import List

def get_same_ids(directory:str=None) -> List[List[str]]:
    """
    Returns a list of Dvks that share the same IDs.
    Files are grouped when they share the same DVK ID.

    :param directory: Directory in which to search, defaults to None
    :type directory: str, optional
    :return: List of Dvks that have identical Dvk IDs
    :rtype: list[list[str]]
    """
    # RETURN EMPTY LIST IF DIRECTORY IS INVALID
    if directory is None or not exists(directory) or not isdir(directory):
        return []
    # READ DVKS IN DIRECTORY
    dvk_handler = DvkHandler()
    dvk_handler.read_dvks(directory)
    dvk_handler.sort_dvks("a")
    # RUN THROUGH ALL DVKS
    indexes = []
    same = []
    size = dvk_handler.get_size()
    print("Finding DVK files with the same IDs:")
    for comp_num in tqdm(range(0, size - 1)):
        comp_dvk = dvk_handler.get_dvk(comp_num)
        current_same = [comp_dvk.get_dvk_file()]
        # ONLY CHECK DUPLICATES IF NOT ALREADY INCLUDED
        if not comp_num in indexes:
            for cur_num in range(comp_num + 1, size):
                cur_dvk = dvk_handler.get_dvk(cur_num)
                # CHECK IF IDS ARE THE SAME
                if (not cur_num in indexes
                        and comp_dvk.get_dvk_id() == cur_dvk.get_dvk_id()):
                    indexes.append(cur_num)
                    current_same.append(cur_dvk.get_dvk_file())
        # ADD GROUP TO SAME ID LIST IF MATCHING IDS FOUND
        if len(current_same) > 1:
            same.append(current_same)
    # RETURN LIST OF DVKS WITH THE SAME ID
    return same

def main():
    """
    Sets up commands for getting DVKs with idendical IDs.
    """
    parser = ArgumentParser()
    parser.add_argument(
            "directory",
            help="Directory in which to search for DVKs with identical ids.",
            nargs="?",
            type=str,
            default=str(getcwd()))
    args = parser.parse_args()
    full_directory = abspath(args.directory)
    # CHECK IF DIRECTORY EXISTS
    if (full_directory is not None
            and exists(full_directory)
            and isdir(full_directory)):
        # GET LIST OF DVKS WITH THE SAME IDS
        same = get_same_ids(full_directory)
        # PRINT LIST
        if len(same) > 0:
            for i in range(0, len(same)):
                print(truncate_path(full_directory, same[i][0]))
                for k in range(1, len(same[i])):
                    print("    " + truncate_path(full_directory, same[i][k]))
        else:
            print("\033[32mAll DVKs have unique IDs.\033[0m")
    else:
        print("Invalid directory")

if __name__ == "__main__":
    main()
