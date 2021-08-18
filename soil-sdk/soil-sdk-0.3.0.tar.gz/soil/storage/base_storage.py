''' Module for BaseStorage '''
from dataclasses import dataclass
from typing import Type, TypeVar, Dict, Any

StorageClass = TypeVar('StorageClass')


@dataclass
class BaseStorage:
    '''
    Abstract class that implements serialize and deserialize methods for storage classes.
    '''
    def serialize(self) -> Dict[str, Any]:
        '''
        Serializes the storage object. In general it shouldn't be used from a module.
        '''

        # TODO if we upgrade to python 3.8 we could use TypedDict
        # https://stackoverflow.com/a/54198204

    @classmethod
    def deserialize(cls: Type[StorageClass], serialized_storage_object: Dict[str, Any]) -> StorageClass:
        '''
        Takes a serialized storage object and returns an instance.
        '''
