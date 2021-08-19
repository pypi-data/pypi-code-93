from proto_formatter.proto import EnumElement
from proto_formatter.proto import Import
from proto_formatter.proto import Message
from proto_formatter.proto import MessageElement
from proto_formatter.proto import Option
from proto_formatter.proto import Package
from proto_formatter.proto import Position
from proto_formatter.proto import ProtoBufStructure
from proto_formatter.proto import ProtoEnum
from proto_formatter.proto import Service
from proto_formatter.proto import ServiceElement
from proto_formatter.proto import Syntax


class Formatter():

    def __init__(self, indents=2, equal_sign=None, all_top_comments=False):
        self.indents = indents
        self.equal_sign = equal_sign
        self.all_top_comments = all_top_comments

    def to_string(self, obj: ProtoBufStructure):
        syntax_string = self.syntax_string(obj.syntax)
        package_string = self.package_string(obj.package)
        option_string = self.options_string(obj.options)
        imports_string = self.imports_string(obj.imports)
        messages_string = self.objects_string(obj.objects)
        contents = [syntax_string, package_string, option_string, imports_string, messages_string]
        contents = list(filter(None, contents))
        content = '\n\n'.join(contents)
        content = content + '\n'

        return content

    def syntax_string(self, obj: Syntax):
        if not obj:
            return ''

        line = f'syntax = "{obj.value}";'
        return self.make_string(line, obj.comments)

    def package_string(self, obj: Package):
        if not obj:
            return ''

        line = f'package {obj.value};'
        return self.make_string(line, obj.comments)

    def options_string(self, obj_list):
        if not obj_list:
            return ''

        max_length = self.max_length_of_option(obj_list)

        string_list = []
        for obj in obj_list:
            string = self.option_string(obj, max_length)
            string_list.append(string)
        return '\n'.join(string_list)

    def max_length_of_option(self, obj_list):
        max = 0
        for obj in obj_list:
            if obj.value == 'true' or obj.value == 'false':
                line = f'option {obj.name} = {obj.value};'
            else:
                line = f'option {obj.name} = "{obj.value}";'

            if max < len(line):
                max = len(line)

        return max

    def option_string(self, obj: Option, max_length):
        if obj.value == 'true' or obj.value == 'false':
            line = f'option {obj.name} = {obj.value};'
        else:
            line = f'option {obj.name} = "{obj.value}";'

        return self.make_string(line, obj.comments, max_length)

    def imports_string(self, obj_list):
        if not obj_list:
            return ''

        max_length = self.max_length_of_import(obj_list)

        string_list = []
        for obj in obj_list:
            string = self.import_string(obj, max_length)
            string_list.append(string)
        return '\n'.join(string_list)

    def max_length_of_import(self, obj_list):
        max = 0
        for obj in obj_list:
            line = f'import "{obj.value}";'

            if max < len(line):
                max = len(line)

        return max

    def import_string(self, obj: Import, max_length):
        line = f'import "{obj.value}";'
        return self.make_string(line, obj.comments, max_length)

    def objects_string(self, obj_list):
        string_list = []
        for obj in obj_list:
            if isinstance(obj, Message):
                string = self.message_string(obj)
            if isinstance(obj, ProtoEnum):
                string = self.enum_string(obj)
            if isinstance(obj, Service):
                string = self.service_string(obj)
            string_list.append(string)
        return '\n\n'.join(string_list)

    def messages_string(self, obj_list):
        string_list = []
        for obj in obj_list:
            string = self.message_string(obj)
            string_list.append(string)
        return '\n\n'.join(string_list)

    def message_string(self, obj: Message):
        line = f'message {obj.name} ' + "{"
        message_header = self.make_string(line, obj.comments)
        elements_string = self.message_elemnents_string(obj.elements)
        s = '\n'.join([message_header, elements_string, '}'])
        return s

    def message_elemnents_string(self, obj_list):
        max_length = self.max_length_of_message_element(obj_list)

        string_list = []
        for obj in obj_list:
            if self.equal_sign:
                string = self.message_elemnent_string_align_with_equal_sign(obj, max_length)
            else:
                string = self.message_elemnent_string(obj, max_length)

            string_list.append(string)
        return '\n'.join(string_list)

    def message_elemnent_string(self, obj: MessageElement, max_length):
        if obj.label:
            line = f'{obj.label} {obj.type} {obj.name} = {obj.number};'
        else:
            line = f'{obj.type} {obj.name} = {obj.number};'

        return self.make_string(line, obj.comments, max_length, indents=self.indents)

    def message_elemnent_string_align_with_equal_sign(self, obj: MessageElement, max_length):
        if obj.label:
            line = f'{obj.label} {obj.type} {obj.name}'
        else:
            line = f'{obj.type} {obj.name}'

        need_fill_space_amount = max_length - len(line)
        line = f'{line}{" " * need_fill_space_amount} = {obj.number};'

        return self.make_string(line, obj.comments, max_length, indents=self.indents)

    def max_length_of_message_element(self, obj_list):
        max = 0
        for obj in obj_list:
            if self.equal_sign:
                if obj.label:
                    line = f'{obj.label} {obj.type} {obj.name}'
                else:
                    line = f'{obj.type} {obj.name}'
            else:
                if obj.label:
                    line = f'{obj.label} {obj.type} {obj.name} = {obj.number};'
                else:
                    line = f'{obj.type} {obj.name} = {obj.number};'

            if max < len(line):
                max = len(line)

        return max

    def enum_string(self, obj: ProtoEnum):
        line = f'enum {obj.name} ' + "{"
        message_header = self.make_string(line, obj.comments)
        elements_string = self.enum_elemnents_string(obj.elements)
        s = '\n'.join([message_header, elements_string, '}'])
        return s

    def enum_elemnents_string(self, obj_list):
        if self.equal_sign:
            max_length = self.max_length_of_enum_element_name(obj_list)
        else:
            max_length = self.max_length_of_enum_element(obj_list)

        string_list = []
        for obj in obj_list:
            string = self.enum_elemnent_string(obj, max_length)
            string_list.append(string)
        return '\n'.join(string_list)

    def enum_elemnent_string(self, obj: EnumElement, max_length):
        if self.equal_sign:
            line = f'{obj.name}'
            need_fill_space_amount = max_length - len(line)
            line = f'{line}{" " * need_fill_space_amount} = {obj.number};'
        else:
            line = f'{obj.name} = {obj.number};'

        return self.make_string(line, obj.comments, max_length, indents=self.indents)

    def max_length_of_enum_element(self, obj_list):
        max = 0
        for obj in obj_list:
            line = f'{obj.name} = {obj.number};'

            if max < len(line):
                max = len(line)

        return max

    def max_length_of_enum_element_name(self, obj_list):
        max = 0
        for obj in obj_list:
            line = f'{obj.name}'

            if max < len(line):
                max = len(line)

        return max

    def service_string(self, obj: ProtoEnum):
        line = f'service {obj.name} ' + "{"
        message_header = self.make_string(line, obj.comments)
        elements_string = self.service_elemnents_string(obj.elements)
        s = '\n'.join([message_header, elements_string, '}'])
        return s

    def service_elemnents_string(self, obj_list):
        max_length = self.max_length_of_service_element(obj_list)

        string_list = []
        for obj in obj_list:
            string = self.service_elemnent_string(obj, max_length)
            string_list.append(string)
        return '\n'.join(string_list)

    def service_elemnent_string(self, obj: ServiceElement, max_length):
        # rpc SeatAvailability (SeatAvailabilityRequest) returns (SeatAvailabilityResponse);
        line = f'{obj.label} {obj.name} ({obj.request}) returns ({obj.response});'

        return self.make_string(line, obj.comments, max_length, indents=self.indents)

    def max_length_of_service_element(self, obj_list):
        max = 0
        for obj in obj_list:
            line = f'{obj.label} {obj.name} ({obj.request}) returns ({obj.response});'

            if max < len(line):
                max = len(line)

        return max

    def make_string(self, value_line, comments, max_length=None, indents=0):
        lines = []
        top_comment_lines = []
        right_comment = ''
        if self.all_top_comments:
            for comment in comments:
                if comment.position == Position.TOP:
                    text_lines = [l.strip() for l in comment.text.split('\n')]
                    top_comment_lines.extend(text_lines)
                if comment.position == Position.Right:
                    top_comment_lines.append(comment.text)
                    right_comment = ''
        else:
            for comment in comments:
                if comment.position == Position.TOP:
                    text_lines = [l.strip() for l in comment.text.split('\n')]
                    top_comment_lines.extend(text_lines)
                if comment.position == Position.Right:
                    right_comment = comment.text

        if top_comment_lines:
            top_comment_lines.insert(0, '/*')
            top_comment_lines.append('*/')

        lines = top_comment_lines
        if right_comment:
            if max_length is not None:
                need_fill_space_amount = max_length - len(value_line)
                line = f'{value_line}{" " * need_fill_space_amount}  // {right_comment}'
            else:
                line = f'{value_line}  // {right_comment}'
            lines.append(line)
        else:
            lines.append(value_line)

        indented_lines = [f'{" " * indents}{line}' for line in lines]
        string = '\n'.join(indented_lines)
        return string
