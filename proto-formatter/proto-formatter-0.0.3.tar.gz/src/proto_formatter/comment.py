from proto_formatter.proto import Comment
from proto_formatter.constant import Constant
from proto_formatter.proto import Position
from proto_formatter.util import remove_prefix, remove_suffix


class CommentParser(Constant):
    def __init__(self):
        self.end_line = 0

        self.multiple_comment_start_symbol_stack = []
        self.multiple_comment_end_symbol_stack = []

    def pick_up_comment(self, lines):
        comment_lines = []
        while lines:
            line = lines.pop(0).strip()

            if self._start_with_multiple_line_comment(line):
                self.multiple_comment_start_symbol_stack.append(self.MULTIPLE_COMENT_START_SYMBOL)
                comment_lines.append(line)
                continue

            if self.is_comment(line):
                comment_lines.append(line)

            if self._end_with_multiple_line_comment(line):
                self.multiple_comment_end_symbol_stack.append(self.MULTIPLE_COMENT_END_SYMBOL)
                continue

            if line and not self.is_comment(line):
                lines.insert(0, line)  # add back
                break

        return comment_lines

    @staticmethod
    def is_not_new_line(variable):
        return variable != '\n'

    def parse(self, comment_lines):
        text = '\n'.join(comment_lines)
        separator = '++++++++++++++++++'
        text = text.replace('/*', separator).replace('*/', separator)
        text_list = text.split(separator)
        text_list = list(filter(None, text_list))
        text_list = list(filter(self.is_not_new_line, text_list))
        text_list = [text.strip().replace(self.SINGLE_COMMENT_SYMBOL, '') for text in text_list]
        multiple_line_comments = text_list
        return multiple_line_comments

    def _start_with_single_line_comment(self, line):
        return line.strip().startswith(self.SINGLE_COMMENT_SYMBOL)

    def _start_with_multiple_line_comment(self, line):
        return line.strip().startswith(self.MULTIPLE_COMENT_START_SYMBOL)

    def _end_with_multiple_line_comment(self, line):
        return line.strip().endswith(self.MULTIPLE_COMENT_END_SYMBOL)

    def _is_multiple_comment(self):
        if len(self.multiple_comment_start_symbol_stack) == 0:
            return False

        return len(self.multiple_comment_start_symbol_stack) > len(self.multiple_comment_end_symbol_stack)

    def is_comment(self, line):
        if self._is_multiple_comment():
            return True

        if self._start_with_single_line_comment(line):
            return True

        return False

    @staticmethod
    def parse_single_line_comment(line):
        comment = None
        if line.count(CommentParser.SINGLE_COMMENT_SYMBOL) > 0:
            start_index = line.index(CommentParser.SINGLE_COMMENT_SYMBOL)
            comment_str = line[start_index:].lstrip(CommentParser.SINGLE_COMMENT_SYMBOL).strip()
            comment = Comment(comment_str, Position.Right)
        return comment

    @staticmethod
    def create_top_comments(comments):
        result = []
        while comments:
            comment_lines = comments.pop(0)
            text = ''.join(comment_lines)
            text = text.strip()
            text = remove_prefix(text, CommentParser.SINGLE_COMMENT_SYMBOL)
            text = remove_prefix(text, CommentParser.MULTIPLE_COMENT_START_SYMBOL)
            text = remove_suffix(text, CommentParser.MULTIPLE_COMENT_END_SYMBOL)
            text = text.strip()
            result.append(Comment(text, Position.TOP))
        return result

    @staticmethod
    def create_comment(line, top_comment_list):
        comments = CommentParser.create_top_comments(top_comment_list)
        right_comment = CommentParser.parse_single_line_comment(line)
        if right_comment is not None:
            comments.append(right_comment)
        return comments
