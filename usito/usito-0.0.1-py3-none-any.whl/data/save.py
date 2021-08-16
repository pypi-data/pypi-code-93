#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 03 2021

@author: AliB
"""

import numpy as np
import os
import re
import math
import shutil
from pathlib import Path
from .utils.image import PngSaver, JpgSaver
from .utils.np import NpySaver, NpzSaver
from .utils.table import CsvSaver, XlsxSaver

_SAVER_MAP = {'.png': PngSaver,
              '.jpg': JpgSaver,
              '.jpeg': JpgSaver,
              '.csv': CsvSaver,
              '.xlsx': XlsxSaver,
              #'.h5': H5Saver, # TODO
              #'.hdf5': H5Saver, # TODO
              '.npy': NpySaver,
              '.npz': NpzSaver}

class FileSaver:
    """Base class for all loaders, specifying their functionality."""
    def __init__(self, path):
        self.path = path
    
    def save(self, array):
        pass
    
    @staticmethod
    def query_dims(arrayshape):
        pass

class NoSaverError(Exception):
    """
    Error specific to the save module: Raised if no saver is assigned.
    """
    pass

def _autosave(array, path, file_type, base_name, mode):
    saver_class = _SAVER_MAP[file_type]
    dims_per_file = saver_class.query_dims(array.shape)
    if dims_per_file and dims_per_file < array.ndim:
        if mode == 'no_interference':
            # Throws an error if file or directory exists which is
            # what we want with no_interference.
            path.mkdir()
        elif mode == 'add':
            # With exist_ok, mkdir only throws said error if target
            # is a file which is, again, the way we want it.
            path.mkdir(exist_ok=True)
        elif mode == 'overwrite':
            # If something exists, delete it, then recreate it.
            if path.exists():
                if path.is_dir():
                    shutil.rmtree(path)
                elif path.is_file() or path.is_symlink():
                    path.unlink()
            path.mkdir()
        ind_len = math.ceil(math.log10(array.shape[0]))
        for index,sl in enumerate(array):
            subpath = path / Path(str(index).zfill(ind_len))
            _autosave(sl, subpath, file_type, base_name, mode)
    else:
        filepath = path.with_name(path.stem+'_'+base_name+file_type)
        if mode == 'overwrite':
            path.unlink(missing_ok=True)
        saver = saver_class(filepath)
        saver.save(array)

    """
    Arguments:
      np_array: The numpy array to be saved.
      path: The path to the file or directory to be saved to.
      file_type: The file type (usually simply the relevant file name
        extension) to save as.  Must be present in the _SAVER_MAP dict.
      base_name: This string will be included in every individual file
        name for easier future reference.
      mode: Defines how existing files or directories are treated.
        - 'no_interference': The safe standard. Do not save anything if
          files or directories exist.
        - 'add': If directories already exist, use them, but do not
          overwrite files.
        - 'overwrite': If directories or files exist, delete and
          overwrite them.
    """

def autosave(np_array, path, file_type='.png', base_name='', 
             mode='no_interference'):
    """
    Given a numpy array, a path and a file type, this function will save the 
    array's contents to disk with the specified type. It is supposed to make 
    reasonable assumptions on how best to save the data given its 
    dimensionality and the target file type.  For example, numpy can save 
    arbitrary arrays as .npy/.npz and the array will therefore be stored as-is.
    Image files, however, have fixed dimensionality and autosave will 
    therefore split the array to end up with images, turning a numpy array 
    with size (100,128,64,3) into 100 color images of 128x64 pixels each.

    Parameters
    ----------
    np_array : nd_array
        The numpy array to be saved.
    path : str
        The path to the file or directory to be saved to.
    file_type : str, optional
        The file type (usually simply the relevant file name extension) to 
        save as. Must be present in the _SAVER_MAP dict. The default is '.png'.
    base_name : str, optional
        This string will be included in every individual file name for easier 
        future reference. The default is ''.
    mode : str, optional
        Defines how existing files or directories are treated.
        - 'no_interference': The safe standard. Do not save anything if files 
            or directories exist.
        - 'add': If directories already exist, use them, but do not overwrite 
            files.
        - 'overwrite': If directories or files exist, delete and overwrite 
            them.
        The default is 'no_interference'.

    Raises
    ------
    NoSaverError
        Raised if no saver is assigned.
    ValueError
        Raised if unknown 'mode'.

    Returns
    -------
    None.

    """
    # Add a dot to the file type if it is not already present.
    if file_type[0] != '.':
        file_type = '.' + file_type
    # Check if file_type fits a registered saver. If not, raise an
    # error.
    try:
        _SAVER_MAP[file_type]
    except KeyError:
        raise NoSaverError("The file type '", file_type, "' does not have "
                           "a saver assigned to it.")
    if mode not in {'no_interference', 'add', 'overwrite'}:
        raise ValueError("Unknown mode: ", mode)
    # Turn the string path into one of pathlib's Path objects.
    plpath = Path(path)
    _autosave(np_array, plpath, file_type, base_name, mode)
 
def _save(array, path, file_type, base_name = "", mode='no_interference', 
          **kwargs):
    saver_class = _SAVER_MAP[file_type]
    dims_per_file = saver_class.query_dims(array.shape)
    if dims_per_file and dims_per_file < array.ndim:
        if mode == 'no_interference':
            # Throws an error if file or directory exists which is
            # what we want with no_interference.
            path.mkdir()
        elif mode == 'add':
            # With exist_ok, mkdir only throws said error if target
            # is a file which is, again, the way we want it.
            path.mkdir(exist_ok=True)
        elif mode == 'overwrite':
            # If something exists, delete it, then recreate it.
            if path.exists():
                if path.is_dir():
                    shutil.rmtree(path)
                elif path.is_file() or path.is_symlink():
                    path.unlink()
            path.mkdir()
        ind_len = math.ceil(math.log10(array.shape[0]))
        for index, sl in enumerate(array):
            subpath = path / Path(str(index).zfill(ind_len))
            _autosave(sl, subpath, file_type, base_name, mode)
    else:
        filepath = path.with_name(path.stem + file_type)
        if not path.parents[0].exists():
            path.parents[0].mkdir(parents = True)
        if mode == 'overwrite':
            path.unlink(missing_ok=True)
        
        saver = saver_class(filepath, **kwargs)
        saver.save(array)
 
def save(array, path, file_type = None, **kwargs):
    """
    Given a path to a file and a multidimensional array, this function will 
    save its contents in the specified file. Compared to autosave() this 
    function enables additional key words for more specific saveing operations 
    (e.g. saving feature names as the header of tables with the keyword 
    'feature_names').

    Parameters
    ----------
    array : ndarray
        Multidimensional array that is to be saved.
    path : str
        The path to where the file is to be saved.
    file_type : TYPE, optional
        DESCRIPTION. The default is None.
    **kwargs : dict
        Only valid key words for the instantiantion of the corresponding 
        saver object are possible. Valid keys can be inspected using the 
        get_valid_keys() function.

    Returns
    -------
    None.

    """
    plpath = Path(path)
    
    if not file_type:
        file_type = plpath.suffix
    
    _saver_check(file_type)
    
    _key_check(path, file_type, **kwargs)
    
    _save(array, plpath, file_type, **kwargs)

def _saver_check(file_type):
    """
    Checks whether the given file type has an associated saver object 
    (specified in _SAVER_MAP).

    Parameters
    ----------
    file_type : str
        The file type (usually simply the relevant file name extension).

    Raises
    ------
    NoLoaderError
        Raised if file type does not have an matching saver object.

    Returns
    -------
    None.

    """
    try:
        _SAVER_MAP[file_type]
    except KeyError:
        raise NoSaverError(f"The file type '{file_type}' does not have a "
                            "saver assigned to it.")

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
    object = _SAVER_MAP[file_type](path = None)
    
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
        _saver_check(file_type)
        object = _SAVER_MAP[file_type](path = None)
        valid_keys[f'{file_type}'] = list(object.__dict__.keys())
    
    else:
        for file_type in _SAVER_MAP.keys():
            object = _SAVER_MAP[file_type](path = None)
            valid_keys[f'{file_type}'] = list(object.__dict__.keys())
    
    return valid_keys