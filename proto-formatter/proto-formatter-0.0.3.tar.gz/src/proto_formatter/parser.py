from enum import Enum

from proto_formatter.constant import Constant
from proto_formatter.comment import CommentParser
from proto_formatter.detector import Detector
from proto_formatter.enum_parser import EnumParser
from proto_formatter.import_parser import ImportParser
from proto_formatter.message_parser import MessageParser
from proto_formatter.option_parser import OptionParser
from proto_formatter.package_parser import PackageParser
from proto_formatter.proto import ProtoBufStructure
from proto_formatter.service_parser import ServiceParser
from proto_formatter.syntax_parser import SyntaxParser
from proto_formatter.util import remove_prefix, remove_suffix


class ProtoParser(Constant):
    def __init__(self):
        self.protobuf_obj = ProtoBufStructure()

    def load(self, fp):
        """
        Load proto from file, deserialize it as a ProtoBufStructure object.
        :param fp: The absolute file path of the proto file.
        :return: Object of ProtoBufStructure.
        """
        lines = self._read_lines(fp)
        return self._parse(lines)

    def loads(self, proto_str):
        """
        Parse proto string, return a ProtoBufStructure object.
        :param proto_str: The proto string need to pasre.
        :return: Object of ProtoBufStructure.
        """
        lines = proto_str.split('\n')
        return self._parse(lines)

    def _read_lines(self, path):
        """
        Read data from file as line list, all blank and empty lines are removed before and after valid text.
        :param path: Absolute file path.
        :return: Line list of the striped file content.
        """
        with open(path) as f:
            content = f.read()
            content = content.strip()
            lines = content.split('\n')
            return lines

    def _parse(self, lines):
        """
        Pasre proto content lines, deserialize them as a ProtoBufStructure object.
        :param lines: the proto content lines.
        :return: an object of ProtoBufStructure.
        """
        keyword, comments = Detector().get_object_type(lines)
        parser = self._get_parser(keyword)
        if parser is None:
            return self.protobuf_obj

        if isinstance(parser, MessageParser):
            parser.parse_and_add(self.protobuf_obj, lines, comments)
        elif isinstance(parser, EnumParser):
            parser.parse_and_add(self.protobuf_obj, lines, comments)
        elif isinstance(parser, ServiceParser):
            parser.parse_and_add(self.protobuf_obj, lines, comments)
        else:
            line = lines.pop(0)
            parser.parse_and_add(self.protobuf_obj, line, comments)

        if len(lines) == 0:
            return self.protobuf_obj

        return self._parse(lines)

    def _get_parser(self, keyword):
        if keyword == 'syntax':
            return SyntaxParser()
        elif keyword == 'package':
            return PackageParser()
        elif keyword == 'option':
            return OptionParser()
        elif keyword == 'import':
            return ImportParser()
        elif keyword == 'message':
            return MessageParser()
        elif keyword == 'enum':
            return EnumParser()
        elif keyword == 'service':
            return ServiceParser()
