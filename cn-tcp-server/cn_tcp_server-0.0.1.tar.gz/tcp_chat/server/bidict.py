class Bidict:
    ''' The simplest class that implements a bijective dict '''

    def __init__(self, init:dict = {}):
        _data = init
        for key in init.keys():
            _data[init[key]] = key
    
    def __setitem__(self, key, value):
        self._data[key] = value
        self._data[value] = key
    
    def __getitem__(self, key):
        return self._data[key]

    def __delitem__(self, key):
        del self._data[self._data[key]]
        del self._data[key]

    def __contains__(self, key):
        return key in self._data
