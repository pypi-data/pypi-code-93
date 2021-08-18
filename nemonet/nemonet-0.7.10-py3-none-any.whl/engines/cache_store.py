import h5py
import chardet
import re

class KeyValueStore(object):

    def __init__(self):
        self.a_cache = h5py.File("cache.hdf5", "a")

    def add(self , key , value):
        self.a_cache.attrs[ key ] = value

    def get_value_as_str(self, key ):
        return self.a_cache.attrs[ key ]

    def close(self):
        self.a_cache.close()

    def replace_formated_key(self, formatted_str):
        m_keys = re.findall(r'(#{.*?})', formatted_str)
        result_fromated_str = formatted_str
        for item in m_keys:
            item_start = 2
            item_end = len(item) - 1
            result_fromated_str = result_fromated_str.replace(item, self.get_value_as_str(item[item_start:item_end]))
        return result_fromated_str