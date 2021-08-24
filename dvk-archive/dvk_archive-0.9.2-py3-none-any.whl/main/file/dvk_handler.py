#!/usr/bin/env python3

from _functools import cmp_to_key
from dvk_archive.main.file.dvk import Dvk
from dvk_archive.main.processing.string_compare import compare_alphanum
from dvk_archive.main.processing.string_compare import compare_strings
from tqdm import tqdm
from typing import List
from os import listdir, walk
from os.path import abspath, exists, isdir, join


def get_directories(directory:str=None, only_dvk:bool=True) -> List[str]:
    """
    Returns a list of sub-directories inside a given directory.
    If specified, only returns directories that contain DVK files.
    Includes the given directory.

    :param directory: Directory to search, defaults to None
    :type directory: str, optional
    :param only_dvk: Whether ot only include directories with DVKs, defaults to True
    :type only_dvk: bool, optional
    :return: Sub-directories of the given directory
    :rtype: list[str]
    """
    # RETURN EMPTY LIST IF GIVEN DIRECTORY IS INVALID
    if directory is None:
        return []
    path = abspath(directory)
    if not exists(path) or not isdir(path):
        return []
    # GET ALL DIRECTORIES AND SUBDIRECTORIES
    dirs = []
    for p in walk(path):
        dirs.append(abspath(p[0]))
    # IF SET TO ONLY RETURN DIRECTORIES WITH DVK FILES,
    # FILTER OUT DIRECTORIES WITHOUT DVK FILES
    if only_dvk:
        i = 0
        while i < len(dirs):
            dvk_dirs = listdir(dirs[i])
            delete = True
            for file in dvk_dirs:
                if file.endswith(".dvk"):
                    delete = False
                    break
            if delete:
                del dirs[i]
                i = i - 1
            # INCREMENT COUNTER
            i = i + 1
    return dirs

class DvkHandler:

    def __init__(self, directory:str=None):
        """
        Initializes the DvkHandler object.
        Loads dvks from a given directory if specified.

        :param directory: Directory from which to load DVKs, defaults to None
        :type directory: str, optional
        """
        self.dvks = []
        if directory is not None:
            self.read_dvks(directory)
    
    def read_dvks(self, directory:str=None):
        """
        Reads all the DVK files in a given directory and stores them in a list.

        :param directory: Directory from which to load DVKs, defaults to None
        :type directory: str, optional
        """
        self.dvks = []
        if directory is not None:
            # GET LIST OF DIRECTORIES CONTAINING DVK FILES
            dirs = get_directories(abspath(directory))
            # LOAD LIST OF DVK FILES
            print("Reading DVK files:")
            for path in tqdm(dirs):
                for file in listdir(path):
                    if file.endswith(".dvk"):
                        dvk = Dvk(abspath(join(path, file)))
                        if dvk.get_title() is not None:
                            self.dvks.append(dvk)

    def sort_dvks(self, sort_type:str=None):
        """
        Sorts all currently loaded DVK objects in the Dvk list.

        :param sort_type: Sort type ("t" = Time, "a" = alphabetical), defaults to None
        :type sort_type: str, optional
        """
        print("Sorting DVK files...")
        if sort_type is not None and self.get_size() > 0:
            if sort_type == "t":
                comparator = cmp_to_key(self.compare_time)
            else:
                comparator = cmp_to_key(self.compare_alpha)
            self.dvks = sorted(self.dvks, key=comparator)

    def compare_time(self, x:Dvk=None, y:Dvk=None) -> int:
        """
        Compare two Dvk objects by their publication time.

        :param x: 1st Dvk object, defaults to None
        :type x: Dvk, optional
        :param y: 2nd Dvk object, defaults to None
        :type y: Dvk, optional
        :return: Which Dvk should come first
        :rtype: int
        """
        # RETURN 0 IF EITHER DVK IS NONE
        if x is None or y is None:
            return 0
        # COMPARE BY TIME
        result = compare_strings(x.get_time(), y.get_time())
        # IF TIMES ARE THE SAME, COMPARE BY TITLE
        if result == 0:
            result = compare_alphanum(x.get_title(), y.get_title())
        return result

    def compare_alpha(self, x:Dvk=None, y:Dvk=None) -> int:
        """
        Compare two Dvk objects alphabetically by title.

        :param x: 1st Dvk object, defaults to None
        :type x: Dvk, optional
        :param y: 2nd Dvk object, defaults to None
        :type y: Dvk, optional
        :return: Which Dvk should come first
        :rtype: int
        """
        # RETURN 0 IF EITHER DVK IS NONE
        if x is None or y is None:
            return 0
        # COMPARE BY TITLE
        result = compare_alphanum(x.get_title(), y.get_title())
        # IF TITLES ARE THE SAME, COMPARE BY TIME
        if result == 0:
            result = compare_strings(x.get_time(), y.get_time())
        return result

    def get_size(self) -> int:
        """
        Gets size of the DVK list.

        :return: Size of the DVK list
        :rtype: int
        """
        return len(self.dvks)

    def get_dvk(self, index:int=0) -> Dvk:
        """
        Returns a Dvk object based on the given index.

        :param index: Index of the Dvk to return, defaults to 0
        :type index: int, optional
        :return: Dvk object from Dvk list
        :rtype: Dvk
        """
        return self.dvks[index]

    def add_dvk(self, dvk:Dvk=None):
        """
        Adds a given Dvk to the DvkHandler's list of Dvks.
        Only adds if Dvk is valid and writable.

        :param dvk: Given Dvk to add, defaults to None
        :type dvk: Dvk, optional
        """
        if dvk is not None and dvk.can_write():
            self.dvks.append(dvk)

    def set_dvk(self, dvk:Dvk=None, index:int=-1):
        """
        Sets the Dvk at a given index.
        Only sets if the Dvk is valid and writable.

        :param dvk: Dvk to set at index, defaults to None
        :type dvk: Dvk, optional
        :param index: Index to set Dvk to, defaults to -1
        :type index: int, optional
        """
        if (dvk is not None
                and dvk.can_write()
                and index > -1
                and index < self.get_size()):
            self.dvks[index] = dvk

    def remove_dvk(self, index:int=-1):
        """
        Removes the Dvk at a given index.

        :param index: Index of the Dvk to remove, defaults to -1
        :type index: int, optional
        """
        if index > -1 and index < self.get_size():
            del self.dvks[index]

    def get_dvk_by_id(self, dvk_id:str=None) -> int:
        """
        Returns the index of the Dvk with the given ID.
        If no Dvk has the given ID, returns -1.

        :param dvk_id: Given Dvk ID, defaults to None
        :type dvk_id: str, optional
        :return: Index of the Dvk with the given ID
        :rtype: int
        """
        # RETURNS -1 IF GIVEN ID IS INVALID
        if dvk_id is None:
            return -1
        # SEARCH FOR GIVEN ID IN LOADED DVKS
        upper_id = dvk_id.upper()
        for i in range(0, self.get_size()):
            if self.get_dvk(i).get_dvk_id() == upper_id:
                return i
        return -1

    def contains_id(self, dvk_id:str=None) -> bool:
        """
        Returns whether there are any Dvk objects with the given Dvk ID.

        :param dvk_id: Given Dvk ID, defaults to None
        :type dvk_id: str, optional
        :return: Whether any loaded Dvk objects contains the given ID
        :rtype: bool
        """
        index = self.get_dvk_by_id(dvk_id)
        if index == -1:
            return False
        return True

    def contains_page_url(self, page_url:str=None) -> bool:
        """
        Returns whether there are any Dvk objects with the given page URL.

        :param page_url: Given page URL, defaults to None
        :type page_url: str, optional
        :return: Whether any loaded Dvk objects contains the given page URL
        :rtype: bool
        """
        # RETURNS FALSE IF GIVEN PAGE URL IS INVALID
        if page_url is None:
            return False
        # SEARCH FOR GIVEN PAGE URL IN LOADED DVKS
        upper_url = page_url.upper()
        for i in range(0, self.get_size()):
            if self.get_dvk(i).get_page_url().upper() == upper_url:
                return True
        return False

    def contains_direct_url(self, direct_url:str=None) -> bool:
        """
        Returns whether there are any Dvk objects with the given direct/secondary URL.

        :param direct_url: Given direct URL, defaults to None
        :type direct_url: str, optional
        :return: Whether any loaded Dvk objects contains the given direct URL
        :rtype: bool
        """
        # RETURNS FALSE IF GIVEN DIRECT URL IS INVALID
        if direct_url is None:
            return False
        # SEARCH FOR GIVEN DIRECT URL IN LOADED DVKS
        upper_url = direct_url.upper()
        for i in range(0, self.get_size()):
            dvk = self.get_dvk(i)
            if ((dvk.get_direct_url() is not None
                    and dvk.get_direct_url().upper() == upper_url)
                    or (dvk.get_secondary_url() is not None
                    and dvk.get_secondary_url().upper() == upper_url)):
                return True
        return False

    def contains_media_file(self, media_file:str=None) -> bool:
        """
        Returns whether there are any Dvk objects that link a given media file.
        Can be primary or secondary media file.

        :param media_file: Given media file, defaults to None
        :type media_file: str, optional
        :return: Whether any loaded Dvk objects link to the given file
        :rtype: bool
        """
        # RETURNS FALSE IF GIVEN MEDIA FILE IS INVALID
        if media_file is None:
            return False
        # SEARCH FOR GIVEN MEDIA FILE IN LOADED DVKS
        path = abspath(media_file)
        for i in range(0, self.get_size()):
            dvk = self.get_dvk(i)
            media = dvk.get_media_file()
            secondary = dvk.get_secondary_file()
            if ((media is not None and media == path)
                    or (secondary is not None and secondary == path)):
                return True
        return False
