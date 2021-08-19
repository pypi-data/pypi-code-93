from enum import Enum
from proto_formatter.constant import Constant
from proto_formatter.comment import CommentParser
from proto_formatter.object_parser import ObjectParser
from proto_formatter.proto import ProtoEnum, EnumElement
from proto_formatter.util import remove_prefix, remove_suffix


class EnumParser(ObjectParser):
    def __init__(self):
        obj = ProtoEnum(name='name', elements=[], comments=[])
        super(EnumParser, self).__init__(obj=obj)

    @classmethod
    def parse_obj_field(cls, line, top_comments=[]):
        line = line.strip()
        equal_sign_index = line.index(cls.EQUAL_SIGN)
        semicolon_index = line.index(cls.SEMICOLON)
        str_before_equqal_sign = line[:equal_sign_index]
        parts = str_before_equqal_sign.split(' ')
        parts = list(filter(None, parts))
        value = line[equal_sign_index + 1:semicolon_index].strip().replace('"', "").replace("'", "")
        comments = CommentParser.create_comment(line, top_comments)
        return EnumElement(name=parts[0], number=value, comments=comments)
