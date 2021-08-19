from enum import Enum

from proto_formatter.comment import CommentParser
from proto_formatter.object_parser import ObjectParser
from proto_formatter.proto import Service
from proto_formatter.proto import ServiceElement
from proto_formatter.util import remove_prefix, remove_suffix


class ServiceParser(ObjectParser):
    def __init__(self):
        obj = Service(name='name', elements=[], comments=[])
        super(ServiceParser, self).__init__(obj=obj)

    @classmethod
    def parse_obj_field(cls, line, top_comments=[]):
        # rpc SeatAvailability (SeatAvailabilityRequest) returns (SeatAvailabilityResponse);
        line = line.strip().replace('(', '')
        line = line.replace(')', '')

        semicolon_index = line.index(cls.SEMICOLON)
        str_before_semicolon = line[:semicolon_index]
        parts = str_before_semicolon.split(' ')
        parts = list(filter(None, parts))
        comments = CommentParser.create_comment(line, top_comments)
        return ServiceElement(label=parts[0], name=parts[1], request=parts[2], response=parts[4], comments=comments)
