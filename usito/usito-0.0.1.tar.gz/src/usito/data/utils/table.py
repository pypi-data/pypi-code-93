# -*- coding: utf-8 -*-
"""
Created on Thu Aug  5 08:57:34 2021

@author: FelixFischer
"""

import numpy as np
import pandas as pd
from .engine import FileLoader, FileSaver

class ShapeMismatch(Exception):
    """
    Error specific to the save module: Raised if shape mismatch.
    """
    pass

class DimensionalityError(Exception):
    """
    Error specific to the save module: Raised if wrong dimensionality.
    """

class TableLoader(FileLoader):
    def __init__(self, path, header = None, label_col = None, sep = ',', 
                 ignore_information = True):
        """
        Loader subclass for all table file types.

        Parameters
        ----------
        path : str or Path object
            Specifies the path of the table object file.
        header : int, optional
            Sets the number of rows to skip until the table content begins. 
            The default is None.
        label_col : int, optional
            Sets the column number of the label column. If set to None, it is
            supposed to be only a data table. The default is None.
        sep : str, optional
            The token that indicates the separation of the tabular entries. 
            The default is ','.
        ignore_information : bool, optional
            If set to 'True', it ignores all possible information regarding
            feature names and labels.

        Returns
        -------
        None.

        """
        super().__init__(path)
        self.header = header
        self.label_col = label_col
        self.sep = sep
        self.ignore_information = ignore_information
    
    def _get_data_from_dataframe(self, df):
        """
        Extracts all data from the given pandas dataframe.

        Parameters
        ----------
        df : DataFrame object
            DataFrame from which the data is extracted.

        Returns
        -------
        data : ndarray or tuple
            If class attribute 'ignore_index' is set to 'True', a numpy data
            array (floats) is returned. Returns a tuple with 'data', 'feature 
            names' and 'labels' otherwise.

        """
        data = df.values
        data = self._object_to_float(data)
        
        if not self.ignore_information:
            data = [data]
            
            if self.header is not None:
                features = df.columns.values.astype(str)
                data.append(features)
            else:
                data.append(None)
            
            if self.label_col is not None:
                labels = df.index.values.astype(str)
                data.append(labels)
            else: 
                data.append(None)
            
            data = tuple(data)
        
        return data
    
    def _object_to_float(self, arr):
        """
        Converts object array into float array (necessary to save storage).

        Parameters
        ----------
        arr : ndarray
            Object array that is transformed.

        Returns
        -------
        arr_trans : ndarray
            Resulting float array.

        """
        arr_trans = np.empty(arr.shape)
        for col in range(arr.shape[1]):
            try:
                arr_trans[:, col] = arr[:, col].astype(float)
            except:
                arr_trans[:, col] = self._categorize(arr[:, col])
        
        arr_trans = arr_trans.astype(float)
        
        return arr_trans
    
    def _categorize(self, arr):
        """
        Encodes string entries into categorical float arrays.
        
        Parameters
        ----------
        arr : ndarray
            Object array that is categorized.

        Returns
        -------
        arr_cat : ndarray
            Categorized float array.

        """
        arr_cat = np.empty(arr.shape) 
        values = np.unique(arr)
        for i, value in enumerate(values):
            arr_cat = np.where(arr == value, i, arr_cat)
        
        return arr_cat
        
    
class CsvLoader(TableLoader):
    """
    This class handles loading table files.
    """
        
    def load(self):
        df = pd.read_csv(self.path, sep = self.sep, header = self.header,
                         index_col = self.label_col)
        
        data = self._get_data_from_dataframe(df)
        
        return data 
    
class XlsxLoader(TableLoader):
    """
    This class handles loading table files.
    """
        
    def load(self):
        df = pd.read_excel(self.path, sep = self.sep, header = self.header,
                           index_col = self.label_col)
        
        data = self._get_data_from_dataframe(df)
        
        return data

        """
        Loader subclass for all table file types.

        Parameters
        ----------
        path : str or Path object
            Specifies the path of the table object file.
        header : int, optional
            Sets the number of rows to skip until the table content begins. 
            The default is None.
        label_col : int, optional
            Sets the column number of the label column. If set to None, it is
            supposed to be only a data table. The default is None.
        sep : str, optional
            The token that indicates the separation of the tabular entries. 
            The default is ','.
        ignore_information : bool, optional
            If set to 'True', it ignores all possible information regarding
            feature names and labels.

        Returns
        -------
        None.

        """
class TableSaver(FileSaver):
    def __init__(self, path, feature_names = None, labels = None, 
                 sep = ','):
        """
        Saver subclass for all table file types.

        Parameters
        ----------
        array : ndarray
            Numpy data array.
        path : str or Path object
            Specifies the path where the table object file shall be saved.
        feature_names : ndarray, optional
            Numpy feature name array. The array has to have the same number of
            features as the number of columns of the data array. The default 
            is None.
        labels : ndarray, optional
            Numpy label array. The array has to have the same number of labels 
            as the number of rows of the data array. The default is None.
        sep : str, optional
            The token that indicates the separation of the tabular entries. 
            The default is ','.

        Returns
        -------
        None.

        """
        super().__init__(path)
        self.feature_names = feature_names
        self.labels = labels
        self.sep = sep
    
    def _get_dataframe(self, array):
        try:
            df = pd.DataFrame(array, columns = self.feature_names, 
                              index = self.labels)
        except:
            raise ShapeMismatch(f"Data array with shape {array.shape} "
                                "does not work out with feature name array of "
                                f"length {len(self.feature_names)} and "
                                "label array with {len(self.labels)}.")
        return df
    
    @staticmethod
    def query_dims(arrayshape):
        # Secures the arrays to have 2 dimensions that it can be saved in a 
        # table.
        return 2

class CsvSaver(TableSaver):
    def save(self, array):
        """
        The actual saving function. It saves a pandas DataFrame object as a 
        '.csv' file.

        Parameters
        ----------
        array : ndarray
            Multidimensional array that is to be saved.

        Raises
        ------
        DimensionalityError
            Raised if dimensionality is inequal to 2.

        Returns
        -------
        None.

        """
        dims = len(array.shape)
        if self.query_dims(dims) != 2:
            raise DimensionalityError(f"Dimensionality of array {dims} does "
                                      "not match '.csv' requirements"
                                      f"({self.query_dims(dims)}).")
        df = self._get_dataframe(array)
        df.to_csv(self.path, sep = self.sep)

class XlsxSaver(TableSaver):
    def save(self, array):
        """
        The actual saving function. It saves a pandas DataFrame object as a 
        '.xlsx' file.

        Parameters
        ----------
        array : ndarray
            Multidimensional array that is to be saved.

        Raises
        ------
        DimensionalityError
            Raised if dimensionality is inequal to 2.

        Returns
        -------
        None.

        """
        dims = len(array.shape)
        if self.query_dims(dims) != 2:
            raise DimensionalityError(f"Dimensionality of array {dims} does "
                                      "not match '.xlsx' requirements"
                                      f"({self.query_dims(dims)}).")
        df = self._get_dataframe(array)
        df.to_excel(self.path)