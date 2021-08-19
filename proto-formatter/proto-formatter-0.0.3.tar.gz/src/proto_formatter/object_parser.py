from enum import Enum
from proto_formatter.detector import Detector
from proto_formatter.comment import CommentParser
from proto_formatter.constant import Constant
from proto_formatter.proto import ProtoBufStructure
from proto_formatter.util import remove_prefix, remove_suffix


class ObjectParser(Constant):

    def __init__(self, obj):
        self.objects = []
        self.cursor = 0

        self.left_brace_stack = []
        self.right_brace_stack = []

        # why elements is shared in multiple instanses when Message(name='name')
        self.obj = obj
        self.debug = 0

    @classmethod
    def _get_obj_name(cls, line):
        parts = line.strip().split(' ')
        parts = list(filter(None, parts))
        name = parts[1]
        return name

    @classmethod
    def parse_obj_field(cls, line, top_comments):
        raise NotImplementedError("Element parse not implemented.")

    def parse_and_add(self, proto_obj: ProtoBufStructure, lines, top_comment_list):
        self.parse(lines, top_comment_list, True)
        proto_obj.objects.append(self.obj)

    def parse(self, lines, top_comments, is_object_start):
        if is_object_start:
            current_line = lines.pop(0)
            name = self._get_obj_name(current_line)
            self.obj.name = name
            self.obj.comments = CommentParser.create_comment(current_line, top_comments)
            return self.parse(lines, [], False)

        parser, comments = Detector().get_object_type(lines)
        current_line = lines.pop(0)
        if Detector()._is_object_end(current_line):
            return

        element = self.parse_obj_field(current_line, comments)
        self.obj.elements.append(element)

        return self.parse(lines, [], False)
