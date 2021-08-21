import logging
from abc import ABC
from collections import Callable
from typing import TypeVar, Dict, Type

from handystuff.imports import construct

logger = logging.getLogger(__name__)

U = TypeVar("U")


class RegistryBase(ABC):
    """The factory class for creating executors"""

    """ Internal registry for available Algorithms """
    registry: Dict[str, U] = None

    @classmethod
    def get_name_of_instance(cls, registree: U) -> str:
        for k, v in cls.registry.items():
            if v == registree.__class__:
                return k
        raise ValueError(f"{registree.__class__.__name__} is not registered!")

    @classmethod
    def get_name_of_type(cls, registree: Type[U]) -> str:
        for k, v in cls.registry.items():
            if v == registree:
                return k
        raise ValueError(f"{registree.__name__} is not registered!")


    @classmethod
    def register(cls, name: str) -> Callable:
        def inner_wrapper(wrapped_class):
            if name in cls.registry:
                logger.warning('Registered item %s already exists. Will replace it', name)
            cls.registry[name] = wrapped_class
            return wrapped_class

        return inner_wrapper

    @classmethod
    def create(cls, name: str, args_as_dict=None, **kwargs):
        """Factory command to create the executor

        Args:
          name: str: 
          args_as_dict:  (Default value = None)
          **kwargs: 

        Returns:

        """

        class_instance = cls.registry.get(name, False)
        if not class_instance:
            raise ValueError(f"No implementation with name {name} exists. "
                             f"Did you forget to @Registry.register it?")
        else:
            object_instance = construct(class_instance, args_as_dict or {}, **kwargs)
            return object_instance
