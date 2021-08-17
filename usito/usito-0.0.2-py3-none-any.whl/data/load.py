#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 03 2021

@author: AliB
"""

import numpy as np
import os
import re
from pathlib import Path
from .utils.image import ImgLoader
from .utils.np import NpyLoader, NpzLoader
from .utils.table import CsvLoader, XlsxLoader

_LOADER_MAP = {'.png': ImgLoader,
               '.jpg': ImgLoader,
               '.jpeg': ImgLoader,
               '.csv': CsvLoader,
               '.xlsx': XlsxLoader,
               #'.h5': H5Loader, # TODO
               #'.hdf5': H5Loader, # TODO
               '.npy': NpyLoader,
               '.npz': NpzLoader}

class NoLoaderError(Exception):
    """
    Error specific to the load module: Raised if no loader is assigned.
    """
    pass
  
def _loader_selector(path, file_type, ignore_unreadable, regex, **kwargs):
    """
    Gets paths to individual files and dispatches the actual loading to the 
    relevant loader instance.

    Parameters
    ----------
    path : Path object
        The path to the file to be loaded..
    file_type : str
        The file_type (usually simply the relevant extension). If None,
        _loader_selector tries to get it from the path. This will fail if the 
        file's extension is non-standard or not yet registered in the 
        _LOADER_MAP dict. Can be overridden by explicitly specifying it.
    ignore_unreadable : bool
        If True, ignore files for which there is no reader available. If False, 
        an error is thrown when such a file is encountered. The default is 
        True.
    regex : str, optional
        Regular expression string to specify matching conditions on the name 
        of any object pointed to directly or within a subdirectory. 
        The default is '.*'.
    **kwargs : dict
        Only valid key words for the instantiantion of the corresponding 
        loader object are possible. Valid keys can be inspected using the 
        get_valid_keys() function.

    Raises
    ------
    NoLoaderError
        Raised if file type does not have an matching loader object.

    Returns
    -------
    Class method.
        Loader method of the associated loader object.

    """
    if file_type is None:
        file_type = path.suffix
    if re.fullmatch(regex, path.name) is None:
        # re.fullmatch returns a match object if it found something and
        # None if it did not.
        return
    try:
        loader = _LOADER_MAP[file_type](path, **kwargs)
    except:
        if not ignore_unreadable:
            # Errors with pre-set file_type are caught in autoload,
            # but for autodetection, errors do not appear any sooner
            # than here, so we need to raise an error here as well.
            raise NoLoaderError("The detected file type '", file_type,
                                "' does not have a loader assigned to it.")
        else:
            return
    return loader.load()

def _autoload(path, file_type, ignore_unreadable, regex):
    if path.is_file():
        return _loader_selector(path, file_type, ignore_unreadable, regex)
    elif path.is_dir():
        elements = []
        for subelement in sorted(path.iterdir()):
            np_element = (
              _autoload(subelement, file_type, ignore_unreadable, regex)
            )
            # _loader_selector (and therefore _autoload) will return
            # None if the file was not read for any reason.  These
            # should not be appended to our list.
            if np_element is not None:
                elements.append(np_element)
        if len(elements) == 0:
            return
        elif len(elements) == 1:
            return elements[0]
        else:
            return np.stack(elements)

def autoload(path, file_type=None, ignore_unreadable=True, regex='.*'):
    """
    Given a path to a file or directory, this function will load its contents 
    into a multidimensional numpy array.

    Parameters
    ----------
    path : TYPE, optional
        The path to the file or directory to be loaded.
    file_type : str, optional
        The file type (usually simply the relevant file name extension). If 
        None, we try to get it from the file names we find themselves. Setting 
        it will force the associated loader regardless of file name. In the 
        latter case, think twice about what you are doing and consider using 
        regex. The default is None.
    ignore_unreadable : bool, optional
        If True, ignore files for which there is no reader available. If False, 
        an error is thrown when such a file is encountered. The default is 
        True.
    regex : str, optional
        Regular expression string to specify matching conditions on the name 
        of any object pointed to directly or within a subdirectory. 
        The default is '.*'.
        For example, to filter for .npz files, use regex '.*\.npz'.
        
        NOTES:
        - The default regex '.*' will match everything, therefore it basically 
          disables the function.
        - We only search for full matches to make the process thorough.
          Therefore, you will need to use wildcards like '.*' to produce
          matches.
        - Python's regexes are similar to Perl's and, sadly, a bit difficult 
          to understand at first. Please see 
          https://docs.python.org/3/library/re.html for documentation.

    Raises
    ------
    NoLoaderError
        Raised if file type does not have an matching loader object.

    Returns
    -------
    result : ndarray
        Multidimensional numpy array.

    """
    if file_type:
        # Add a dot to the file type if it is not already present.
        if file_type[0] != '.':
            file_type = '.' + file_type
        # Check if file_type fits a registered loader. If not, raise an
        # error.
        _loader_check(file_type)
        
    # Turn the string path into one of pathlib's Path objects.
    plpath = Path(path)
    result = _autoload(plpath, file_type, ignore_unreadable, regex)
    
    if result is None:
        print("No matching data could be found.")
    
    return result

def _load(path, file_type, **kwargs):
    if path.is_file():
        return _loader_selector(path, file_type, ignore_unreadable=False, 
                                regex='.*', **kwargs)
    else:
        raise TypeError(f"Specified path {str(path)} is not a file.")
    
def load(path, **kwargs):
    """
    Given a path to a file, this function will load its contents into a 
    multidimensional numpy array. Compared to autoload() this function enables
    additional key words for more specific loading operations (e.g. choosing 
    header size of tables with the keyword 'header').

    Parameters
    ----------
    path : str or Path object
        The path to the file to be loaded.
    **kwargs : dict
        Only valid key words for the instantiantion of the corresponding 
        loader object are possible. Valid keys can be inspected using the 
        get_valid_keys() function.

    Returns
    -------
    result : ndarray or tuple
        Multidimensional numpy array or tuple of arrays.

    """
    plpath = Path(path)
    file_type = plpath.suffix
    
    _loader_check(file_type)
    
    _key_check(path, file_type, **kwargs)
    
    result = _load(plpath, file_type, **kwargs)
    
    if result is None:
        print("No matching data could be found.")
    
    return result

def _loader_check(file_type):
    """
    Checks whether the given file type has an associated loader object 
    (specified in _LOADER_MAP).

    Parameters
    ----------
    file_type : str
        The file type (usually simply the relevant file name extension).

    Raises
    ------
    NoLoaderError
        Raised if file type does not have an matching loader object.

    Returns
    -------
    None.

    """
    try:
        _LOADER_MAP[file_type]
    except KeyError:
        raise NoLoaderError(f"The file type '{file_type}' does not have a "
                            "loader assigned to it.")

def _key_check(path, file_type, **kwargs):
    """
    Checks whether all kwargs are valid for the specified file type.

    Parameters
    ----------
    path : Path object
        The path to the file or directory to be loaded.
    file_type : str
        The file type (usually simply the relevant file name extension).
    **kwargs : dict
        Only valid key words for the instantiantion of the corresponding 
        loader object are possible.

    Raises
    ------
    KeyError
        Raised if invalid key is found.

    Returns
    -------
    None.

    """
    object = _LOADER_MAP[file_type](path = None)
    
    for key in kwargs:
        if key not in object.__dict__.keys():
            raise KeyError(f"'{key}' is not a valid argument for loading a "
                           f"'{file_type}' file.")

def get_valid_keys(file_type = None):
    """
    This function is for the case that one does not know what keys are allowed 
    for the loading and saving options. All (or the requested) valid keys are 
    displayed.

    Parameters
    ----------
    file_type : str, optional
        The file type (usually simply the relevant file name extension).If 
        None, the function will simply display all possible file types and the
        associated keys. The default is None.

    Returns
    -------
    valid_keys : dict
        A dictionary with requested file types and the associated valid keys.

    """
    valid_keys = {}
    
    if file_type:
        # Add a dot to the file type if it is not already present.
        if file_type[0] != '.':
            file_type = '.' + file_type
        _loader_check(file_type)
        object = _LOADER_MAP[file_type](path = None)
        valid_keys[f'{file_type}'] = list(object.__dict__.keys())
    
    else:
        for file_type in _LOADER_MAP.keys():
            object = _LOADER_MAP[file_type](path = None)
            valid_keys[f'{file_type}'] = list(object.__dict__.keys())
    
    return valid_keys
    