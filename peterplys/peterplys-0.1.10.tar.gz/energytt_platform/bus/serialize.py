from serpyco import field
from dataclasses import dataclass
from typing import Generic, TypeVar, Union, Dict, Any, Optional

from energytt_platform.serialize import json_serializer, simple_serializer

from .broker import Message
from .registry import message_registry


TWrappedMessage = TypeVar('TWrappedMessage', bound=Message)
TSerializedMessage = Dict[str, Any]


@dataclass
class MessageWrapper(Message, Generic[TWrappedMessage]):
    """
    TODO
    """
    type_: str = field(dict_key='type')
    msg: Optional[Union[TWrappedMessage, TSerializedMessage]] = field(default=None)


class MessageSerializer(object):
    """
    A serializer specifically for serializing messages to
    and from the event bus.
    """

    class MessageSerializeError(Exception):
        """
        TODO
        """
        pass

    class MessageDeserializeError(Exception):
        """
        TODO
        """
        pass

    def serialize(self, msg: Message) -> bytes:
        """
        Wraps message appropriately and JSON serializes it.
        """
        if msg not in message_registry:
            raise self.MessageSerializeError((
                f'Can not serialize of type "{msg.__class__.__name__}": '
                'Type is unknown to the bus.'
            ))

        wrapped_msg = MessageWrapper(
            type_=msg.__class__.__name__,
            msg=msg,
        )

        return json_serializer.serialize(
            obj=wrapped_msg,
            cls=MessageWrapper[msg.__class__],
        )

    def deserialize(self, data: bytes) -> Message:
        """
        Deserializes JSON bytestream into a message.
        """
        wrapped_msg = json_serializer.deserialize(
            data=data,
            cls=MessageWrapper[TSerializedMessage],
        )

        if wrapped_msg.type_ not in message_registry:
            raise self.MessageDeserializeError((
                f'Can not deserialize message of type "{wrapped_msg.type_}": '
                'Type is unknown to the bus.'
            ))

        message_cls = message_registry.get(wrapped_msg.type_)

        return simple_serializer.deserialize(
            data=wrapped_msg.msg,
            cls=message_cls,
        )

# class MessageSerializerOLD(object):
#     """
#     A serializer specifically for serializing messages to
#     and from the event bus.
#     """
#
#     SEPARATOR = b'\n'
#
#     def __init__(self):
#         self.serializer = JsonSerializer()
#
#     def serialize(self, msg: Serializable) -> bytes:
#         if msg.type_name not in registry:
#             raise RuntimeError((
#                 'Can not send message of type "%s": '
#                 'Type is not known by the bus.'
#             ) % msg.type_name)
#
#         return b'%b%b%b' % (
#             msg.type_name.encode(),
#             self.SEPARATOR,
#             self.serializer.serialize(msg),
#         )
#
#     def deserialize(self, data: bytes) -> Serializable:
#         separator_index = data.find(self.SEPARATOR)
#         object_name = data[:separator_index].decode('utf8')
#         object_class = registry[object_name]
#         object_data = data[separator_index+1:]
#
#         return self.serializer.deserialize(object_data, object_class)
