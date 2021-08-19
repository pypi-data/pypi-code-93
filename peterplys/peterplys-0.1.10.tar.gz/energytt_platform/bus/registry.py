from inspect import isclass
from typing import Dict, Union, Type, Optional

# from energytt_platform.serialize import Serializable

from .broker import Message


class MessageRegistry(Dict[str, Type[Message]]):
    """
    A registry of all messages that the bus knows of.

    Works a a dict where:
        Key = Message type name (str)
        Value = Message class (Serializable)

    TODO Enforce unique names
    """

    @classmethod
    def from_message_types(cls, *message_types: Type[Message]) -> 'MessageRegistry':
        return cls({c.__name__: c for c in message_types})

    def add(self, *message_types: Type[Message]):
        self.update({c.__name__: c for c in message_types})

    def __contains__(self, item: Union[str, Message, Type[Message]]) -> bool:
        """
        Check whether an item is known by the registry.

        Item can be either of the following:
            - A string (name of the message type)
            - A class type (the message type itself)
            - An instance of a class (an instance of a message type)
        """
        if isinstance(item, str):
            return item in self.keys()
        elif isclass(item) and issubclass(item, Message):
            return item in self.values()
        elif isinstance(item, Message):
            return item.__class__ in self.values()
        else:
            return False

    def get(self, item: Union[str, Message, Type[Message]]) -> Optional[Message]:
        """
        TODO
        """
        if isinstance(item, str):
            return super(MessageRegistry, self).get(item)
        elif isclass(item) and issubclass(item, Message):
            return super(MessageRegistry, self).get(item.__name__)
        elif isinstance(item, Message):
            return super(MessageRegistry, self).get(item.__class__.__name__)
        else:
            raise RuntimeError('TODO')


# -- Singletons --------------------------------------------------------------


# Singleton message registry TODO
message_registry = MessageRegistry()
