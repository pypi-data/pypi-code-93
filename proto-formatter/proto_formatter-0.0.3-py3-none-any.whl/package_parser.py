from proto_formatter.comment import CommentParser
from proto_formatter.proto import Package
from proto_formatter.proto import ProtoBufStructure


class PackageParser():

    @classmethod
    def parse_and_add(cls, proto_obj: ProtoBufStructure, line, top_comment_list):
        if proto_obj.package is not None:
            raise 'multiple package detected!'

        proto_obj.package = cls.parse_package(line, top_comment_list)

    @classmethod
    def parse_package(self, line, top_comment_list):
        value = self._get_package_value(line)
        comments = CommentParser.create_comment(line, top_comment_list)
        package = Package(value, comments)
        return package

    @classmethod
    def _get_package_value(self, line):
        line = line.strip()
        lindex = len('package ')
        rindex = line.index(';')
        value = line[lindex:rindex].strip()
        return value
