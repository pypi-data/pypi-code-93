#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 03 2021

@author: AliB
"""

import numpy as np
from .engine import FileLoader, FileSaver

class NpyLoader(FileLoader):
    """This class handles loading standard .npy files."""
    def load(self):
        return np.load(self.path)

class NpzLoader(FileLoader):
    """This class handles loading multi-array .npz files.  It does so
    without further intelligence, simply attaching all arrays it finds
    to one another and returning this construct.
    """
    def load(self):
        with np.load(self.path) as data:
            arr_list = []
            for arr in data.files:
                arr_list.append(data[arr])
        return np.concatenate(arr_list)

class NumpySaver(FileSaver):
    @staticmethod
    def query_dims(arrayshape):
        return None

class NpySaver(NumpySaver):
    def save(self, array):
        np.save(self.path, array)

class NpzSaver(NumpySaver):
    def save(self, array):
        np.savez_compressed(self.path, array)
