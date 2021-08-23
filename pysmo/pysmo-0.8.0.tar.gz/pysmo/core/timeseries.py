"""
Python module for reading/writing pysmo files using the :class:`TimeSeries` class.
"""
import os
import h5py
import numpy as np

class TimeSeries():
    """
    Hierarchy:
        /data                   # current data
        /metadata               # current metadata
        /metadata/native        # native metadata
        /metadata/imported      # imported metadata for which there is no mapping to native
        /metadata/user          # user defined metadata (e.g. for applications)
        /snapshots              # snapshots consist of unique identifier for snapshot, datasnapID and metasnapID
        /snapshots/datasnaps    #
        /snapshots/metasnaps

    """

    def __init__(self, filename=None):
        self._data = np.array([])
        self._metadata = {}
        self._snapshots = []
        if filename is not None:
            if os.path.isfile(filename):
                self.readfile
            else:
                self.initfile

    def readfile(self):
        with h5py.File(self.filename, 'r') as f:
            self._data = f['data']
            self._metadata = f['metadata']
            self._snapshots = f['snapshots'].keys

   
    def initfile(self):
        with h5py.File(self.filename, 'a') as f:
            f['data'] = self._data

    @property
    def data(self):
        # Data is stored as _data inside the object
        return self._data

    @data.setter
    def data(self, data):
        # Data is stored as _data inside the object
        self._data = data

    @property
    def snapshots(self):
        return self._snapshots
