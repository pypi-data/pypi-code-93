# -*- coding: utf-8 -*-
#Copyright (c) 2020, KarjaKAK
#All rights reserved.

import json
import os
from collections.abc import Iterator
from types import GeneratorType
from typing import Union, Any

class Datab:
    """
    Database created in json file.
    """
    __slots__ = '__path',
    
    def __init__(self, pname: str):
        if isinstance(pname, str):
            self.__path = f'{pname}.json' if '.json' not in pname else pname
        else:
            raise TypeError('{pname} must be string!')
    
    def __getattribute__(self, name):
        return super().__getattribute__(name)
    
    def __getattr__(self, name):
        if name == 'pname':
            return self.__path
        raise AttributeError(f'"{name}" is not exist!')    
    
    def __repr__(self):
        return f'Datab(pname = {self.__path})'
    
    def validate(self):
        """Validate Path"""
        
        if os.path.exists(self.__path):
            return True
        raise FileNotFoundError('File is not exist yet!')
        
    
    def createdb(self, data: Union[Iterator, GeneratorType]) -> None:
        """Create first time database."""
        
        try:
            if isinstance(data, (Iterator, GeneratorType)):
                try:
                    if not os.path.exists(self.__path):
                        with open(self.__path, 'w') as dbj:
                            json.dump(dict(data), dbj)
                    else:
                        raise FileExistsError('File already exist!')
                except Exception as e:
                    raise e
            else:
                raise TypeError('Must be Generator or iterator')
        except Exception as e:
            raise e
        finally:
            del data
    
    def indata(self, data: Union[Iterator, GeneratorType]) -> None:
        """Insert data to existing database."""
        
        try:
            adb = None
            if isinstance(data, (Iterator, GeneratorType)):
                if self.validate():
                    with open(self.__path) as rdb:
                        adb = iter(dict(json.load(rdb)).items())
                    with open(self.__path, 'w') as dbj:
                        json.dump(dict(adb) | dict(data), dbj)
            else:
                raise TypeError('Must be Generator or iterator')
        except Exception as e:
            raise e
        finally:
            del data, adb        
    
    def deldata(self, named: str) -> None:
        """Delete a data in existing database."""
        
        try:
            adb = None
            if isinstance(named, str):
                if self.validate():
                    with open(self.__path) as rdb:
                        adb = dict(json.load(rdb))
                    if named in adb:
                        del adb[named]
                        with open(self.__path, 'w') as dbj:
                            json.dump(adb, dbj)
                    else:
                        raise KeyError('Key not found in database!')
            else:
                raise TypeError('Must be str')
        except Exception as e:
            raise e
        finally:
            del named, adb
    
    def takedat(self, named: str) -> Any:
        """Taking a data from database."""
        
        try:
            adb = None
            if isinstance(named, str):
                if self.validate():
                    with open(self.__path) as rdb:
                        adb = dict(json.load(rdb))
                    if named in adb:
                        return adb[named]
                    else:
                        raise KeyError('Key not found in database!')
            else:
                raise TypeError('Must be str')
        except Exception as e:
            raise e
        finally:
            del named, adb
            
    def totalrecs(self) -> int:
        """Return the total of records in database."""
        
        try:
            adb = None
            if self.validate():
                with open(self.__path) as rdb:
                    adb = len(dict(json.load(rdb)))
                return adb
        except Exception as e:
            raise e
        
    def deldb(self) -> None:
        """Delete database."""
        
        if self.validate():
            os.remove(self.__path)
    
    def loadall(self) -> 'dict_items':
        """Load all database to dictionary's items."""
        
        try:
            adb = None
            if self.validate():
                with open(self.__path) as rdb:
                    adb = dict(json.load(rdb)).items()
                return adb
        except Exception as e:
            raise e
        finally:
            del adb
            
    def loadkeys(self) -> 'dict_keys':
        """Load all database keys only."""
        
        try:
            adb = None
            if self.validate():
                with open(self.__path) as rdb:
                    adb = dict(json.load(rdb)).keys()
                return adb
        except Exception as e:
            raise e
        finally:
            del adb        
    
    def loadvalues(self) -> 'dict_values':
        """Load all database values only."""
        
        try:
            adb = None
            if self.validate():
                with open(self.__path) as rdb:
                    adb = dict(json.load(rdb)).values()
                return adb
        except Exception as e:
            raise e
        finally:
            del adb         
                
if __name__ == '__main__':
    #a = Datab(os.getcwd()+'\\Mantap')
    #print(a.pname, repr(a), a)
    a = Datab(os.path.join(os.getcwd(),'coba'))
    
    print(a)
    a.createdb(iter({'mantaaap': 'keren'}.items()))
    a.indata(iter({'keren': 'mantaaap'}.items()))
    print(a.totalrecs())
    print(list(a.loadall()))
    print(list(a.loadkeys()))
    print(list(a.loadvalues()))
    print(a.takedat('keren'))
    a.deldata('mantaaap')
    print(a.loadall())
    print(a.totalrecs())
    a.deldb()