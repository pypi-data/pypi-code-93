#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 03 2021

@author: AliB
"""

import numpy as np
from PIL import Image
from .engine import FileLoader, FileSaver

class ImgLoader(FileLoader):
    """This class handles loading image files. See
    https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html
    for all supported file types.
    """
    def load(self):
        im = Image.open(self.path, 'r')
        return np.asarray(im)

class ImgSaver(FileSaver):
    def save(self, array):
        if array.ndim == 3 and array.size[-1] == 1:
            im = Image.fromarray(array[:-1], mode='L')
        elif array.ndim == 3 and array.size[-1] == 3:
            im = Image.fromarray(array, mode='RGB')
        elif array.ndim == 3 and array.size[-1] == 4:
            im = Image.fromarray(array, mode='RGBA')
        elif array.ndim == 2:
            im = Image.fromarray(array, mode='L')
        else:
            raise ValueError("Input array has an unexpected shape")
        im.save(self.path, self.FORMAT)
  
    @staticmethod
    def query_dims(arraysize):
        # If the last dimension is of size 1, 3 or 4, consider it the
        # channels (greyscale, color, color+alpha) and accept 3 dims.
        # Else, consider it greyscale with the channels missing and
        # accept 2 dims.
        if arraysize[-1] in (1,3,4):
            return 3
        else:
            return 2

class PngSaver(ImgSaver):
    FORMAT = 'PNG'

class JpgSaver(ImgSaver):
    FORMAT = 'JPG'
