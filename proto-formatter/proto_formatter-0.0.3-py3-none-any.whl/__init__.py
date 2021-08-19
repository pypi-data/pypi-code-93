from proto_formatter.formatter import Formatter
from proto_formatter.parser import ProtoParser


def format_file(fp, indents=2, all_top_comments=False, equal_sign=False, new_fp=None):
    """
    Format protobuf file, override the original file if no new file path(new_fp) specified
    or write the formatted result to a new file.
    :param fp: unformatted protobuf file path.
    :param indents: indents number.
    :param all_top_comments: convert the single line comment at the left of code as a top comment or not. Default: not
    :param equal_sign: if align the code by equal sign or not.
    Example of align:
        ENUM_TYPE_UNSPECIFIED = 0;  // ENUM_TYPE_UNSPECIFIED
        ENUM_TYPE_CARRY_A     = 1;  // ENUM_TYPE_CARRY_A
        ENUM_TYPE_B           = 2;  // ENUM_TYPE_B
    :param new_fp: the file path of new formatted protobuf file. Rewrite the original file if it is not specified.
    :return: file content size.
    """
    parser = ProtoParser()
    protobuf_obj = parser.load(fp=fp)
    formatter = Formatter(indents=indents, all_top_comments=all_top_comments, equal_sign=equal_sign)
    content = formatter.to_string(protobuf_obj)

    if new_fp:
        fp = new_fp

    with open(fp, 'w') as f:
        return f.write(content)

def format_str(proto_str, indents=2, all_top_comments=False, equal_sign=False):
    """
    Format a protobuf string, return the formatted string.
    :param proto_str: protobuf string need to be formatted.
    :param indents: indents number.
    :param all_top_comments: convert the single line comment at the left of code as a top comment or not. Default: not
    :param equal_sign: if align the code by equal sign or not.
    Example of align:
        ENUM_TYPE_UNSPECIFIED = 0;  // ENUM_TYPE_UNSPECIFIED
        ENUM_TYPE_CARRY_A     = 1;  // ENUM_TYPE_CARRY_A
        ENUM_TYPE_B           = 2;  // ENUM_TYPE_B
    :return: formatted string.
    """
    parser = ProtoParser()
    protobuf_obj = parser.loads(proto_str=proto_str.strip())
    formatter = Formatter(indents=indents, all_top_comments=all_top_comments, equal_sign=equal_sign)

    return formatter.to_string(protobuf_obj)

