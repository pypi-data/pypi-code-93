"""
    pygments.lexers.data
    ~~~~~~~~~~~~~~~~~~~~

    Lexers for data file format.

    :copyright: Copyright 2006-2021 by the Pygments team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

import re

from pygments.lexer import Lexer, RegexLexer, ExtendedRegexLexer, LexerContext, \
    include, bygroups, inherit
from pygments.token import Text, Comment, Keyword, Name, String, Number, \
    Punctuation, Literal, Error

__all__ = ['YamlLexer', 'JsonLexer', 'JsonBareObjectLexer', 'JsonLdLexer']


class YamlLexerContext(LexerContext):
    """Indentation context for the YAML lexer."""

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.indent_stack = []
        self.indent = -1
        self.next_indent = 0
        self.block_scalar_indent = None


class YamlLexer(ExtendedRegexLexer):
    """
    Lexer for `YAML <http://yaml.org/>`_, a human-friendly data serialization
    language.

    .. versionadded:: 0.11
    """

    name = 'YAML'
    aliases = ['yaml']
    filenames = ['*.yaml', '*.yml']
    mimetypes = ['text/x-yaml']

    def something(token_class):
        """Do not produce empty tokens."""
        def callback(lexer, match, context):
            text = match.group()
            if not text:
                return
            yield match.start(), token_class, text
            context.pos = match.end()
        return callback

    def reset_indent(token_class):
        """Reset the indentation levels."""
        def callback(lexer, match, context):
            text = match.group()
            context.indent_stack = []
            context.indent = -1
            context.next_indent = 0
            context.block_scalar_indent = None
            yield match.start(), token_class, text
            context.pos = match.end()
        return callback

    def save_indent(token_class, start=False):
        """Save a possible indentation level."""
        def callback(lexer, match, context):
            text = match.group()
            extra = ''
            if start:
                context.next_indent = len(text)
                if context.next_indent < context.indent:
                    while context.next_indent < context.indent:
                        context.indent = context.indent_stack.pop()
                    if context.next_indent > context.indent:
                        extra = text[context.indent:]
                        text = text[:context.indent]
            else:
                context.next_indent += len(text)
            if text:
                yield match.start(), token_class, text
            if extra:
                yield match.start()+len(text), token_class.Error, extra
            context.pos = match.end()
        return callback

    def set_indent(token_class, implicit=False):
        """Set the previously saved indentation level."""
        def callback(lexer, match, context):
            text = match.group()
            if context.indent < context.next_indent:
                context.indent_stack.append(context.indent)
                context.indent = context.next_indent
            if not implicit:
                context.next_indent += len(text)
            yield match.start(), token_class, text
            context.pos = match.end()
        return callback

    def set_block_scalar_indent(token_class):
        """Set an explicit indentation level for a block scalar."""
        def callback(lexer, match, context):
            text = match.group()
            context.block_scalar_indent = None
            if not text:
                return
            increment = match.group(1)
            if increment:
                current_indent = max(context.indent, 0)
                increment = int(increment)
                context.block_scalar_indent = current_indent + increment
            if text:
                yield match.start(), token_class, text
                context.pos = match.end()
        return callback

    def parse_block_scalar_empty_line(indent_token_class, content_token_class):
        """Process an empty line in a block scalar."""
        def callback(lexer, match, context):
            text = match.group()
            if (context.block_scalar_indent is None or
                    len(text) <= context.block_scalar_indent):
                if text:
                    yield match.start(), indent_token_class, text
            else:
                indentation = text[:context.block_scalar_indent]
                content = text[context.block_scalar_indent:]
                yield match.start(), indent_token_class, indentation
                yield (match.start()+context.block_scalar_indent,
                       content_token_class, content)
            context.pos = match.end()
        return callback

    def parse_block_scalar_indent(token_class):
        """Process indentation spaces in a block scalar."""
        def callback(lexer, match, context):
            text = match.group()
            if context.block_scalar_indent is None:
                if len(text) <= max(context.indent, 0):
                    context.stack.pop()
                    context.stack.pop()
                    return
                context.block_scalar_indent = len(text)
            else:
                if len(text) < context.block_scalar_indent:
                    context.stack.pop()
                    context.stack.pop()
                    return
            if text:
                yield match.start(), token_class, text
                context.pos = match.end()
        return callback

    def parse_plain_scalar_indent(token_class):
        """Process indentation spaces in a plain scalar."""
        def callback(lexer, match, context):
            text = match.group()
            if len(text) <= context.indent:
                context.stack.pop()
                context.stack.pop()
                return
            if text:
                yield match.start(), token_class, text
                context.pos = match.end()
        return callback

    tokens = {
        # the root rules
        'root': [
            # ignored whitespaces
            (r'[ ]+(?=#|$)', Text),
            # line breaks
            (r'\n+', Text),
            # a comment
            (r'#[^\n]*', Comment.Single),
            # the '%YAML' directive
            (r'^%YAML(?=[ ]|$)', reset_indent(Name.Tag), 'yaml-directive'),
            # the %TAG directive
            (r'^%TAG(?=[ ]|$)', reset_indent(Name.Tag), 'tag-directive'),
            # document start and document end indicators
            (r'^(?:---|\.\.\.)(?=[ ]|$)', reset_indent(Name.Namespace),
             'block-line'),
            # indentation spaces
            (r'[ ]*(?!\s|$)', save_indent(Text, start=True),
             ('block-line', 'indentation')),
        ],

        # trailing whitespaces after directives or a block scalar indicator
        'ignored-line': [
            # ignored whitespaces
            (r'[ ]+(?=#|$)', Text),
            # a comment
            (r'#[^\n]*', Comment.Single),
            # line break
            (r'\n', Text, '#pop:2'),
        ],

        # the %YAML directive
        'yaml-directive': [
            # the version number
            (r'([ ]+)([0-9]+\.[0-9]+)',
             bygroups(Text, Number), 'ignored-line'),
        ],

        # the %TAG directive
        'tag-directive': [
            # a tag handle and the corresponding prefix
            (r'([ ]+)(!|![\w-]*!)'
             r'([ ]+)(!|!?[\w;/?:@&=+$,.!~*\'()\[\]%-]+)',
             bygroups(Text, Keyword.Type, Text, Keyword.Type),
             'ignored-line'),
        ],

        # block scalar indicators and indentation spaces
        'indentation': [
            # trailing whitespaces are ignored
            (r'[ ]*$', something(Text), '#pop:2'),
            # whitespaces preceding block collection indicators
            (r'[ ]+(?=[?:-](?:[ ]|$))', save_indent(Text)),
            # block collection indicators
            (r'[?:-](?=[ ]|$)', set_indent(Punctuation.Indicator)),
            # the beginning a block line
            (r'[ ]*', save_indent(Text), '#pop'),
        ],

        # an indented line in the block context
        'block-line': [
            # the line end
            (r'[ ]*(?=#|$)', something(Text), '#pop'),
            # whitespaces separating tokens
            (r'[ ]+', Text),
            # key with colon
            (r'''([^#,:?\[\]{}"'\n]+)(:)(?=[ ]|$)''',
             bygroups(Name.Tag, set_indent(Punctuation, implicit=True))),
            # tags, anchors and aliases,
            include('descriptors'),
            # block collections and scalars
            include('block-nodes'),
            # flow collections and quoted scalars
            include('flow-nodes'),
            # a plain scalar
            (r'(?=[^\s?:,\[\]{}#&*!|>\'"%@`-]|[?:-]\S)',
             something(Name.Variable),
             'plain-scalar-in-block-context'),
        ],

        # tags, anchors, aliases
        'descriptors': [
            # a full-form tag
            (r'!<[\w#;/?:@&=+$,.!~*\'()\[\]%-]+>', Keyword.Type),
            # a tag in the form '!', '!suffix' or '!handle!suffix'
            (r'!(?:[\w-]+!)?'
             r'[\w#;/?:@&=+$,.!~*\'()\[\]%-]*', Keyword.Type),
            # an anchor
            (r'&[\w-]+', Name.Label),
            # an alias
            (r'\*[\w-]+', Name.Variable),
        ],

        # block collections and scalars
        'block-nodes': [
            # implicit key
            (r':(?=[ ]|$)', set_indent(Punctuation.Indicator, implicit=True)),
            # literal and folded scalars
            (r'[|>]', Punctuation.Indicator,
             ('block-scalar-content', 'block-scalar-header')),
        ],

        # flow collections and quoted scalars
        'flow-nodes': [
            # a flow sequence
            (r'\[', Punctuation.Indicator, 'flow-sequence'),
            # a flow mapping
            (r'\{', Punctuation.Indicator, 'flow-mapping'),
            # a single-quoted scalar
            (r'\'', String, 'single-quoted-scalar'),
            # a double-quoted scalar
            (r'\"', String, 'double-quoted-scalar'),
        ],

        # the content of a flow collection
        'flow-collection': [
            # whitespaces
            (r'[ ]+', Text),
            # line breaks
            (r'\n+', Text),
            # a comment
            (r'#[^\n]*', Comment.Single),
            # simple indicators
            (r'[?:,]', Punctuation.Indicator),
            # tags, anchors and aliases
            include('descriptors'),
            # nested collections and quoted scalars
            include('flow-nodes'),
            # a plain scalar
            (r'(?=[^\s?:,\[\]{}#&*!|>\'"%@`])',
             something(Name.Variable),
             'plain-scalar-in-flow-context'),
        ],

        # a flow sequence indicated by '[' and ']'
        'flow-sequence': [
            # include flow collection rules
            include('flow-collection'),
            # the closing indicator
            (r'\]', Punctuation.Indicator, '#pop'),
        ],

        # a flow mapping indicated by '{' and '}'
        'flow-mapping': [
            # key with colon
            (r'''([^,:?\[\]{}"'\n]+)(:)(?=[ ]|$)''',
             bygroups(Name.Tag, Punctuation)),
            # include flow collection rules
            include('flow-collection'),
            # the closing indicator
            (r'\}', Punctuation.Indicator, '#pop'),
        ],

        # block scalar lines
        'block-scalar-content': [
            # line break
            (r'\n', Text),
            # empty line
            (r'^[ ]+$',
             parse_block_scalar_empty_line(Text, Name.Constant)),
            # indentation spaces (we may leave the state here)
            (r'^[ ]*', parse_block_scalar_indent(Text)),
            # line content
            (r'[\S\t ]+', Name.Constant),
        ],

        # the content of a literal or folded scalar
        'block-scalar-header': [
            # indentation indicator followed by chomping flag
            (r'([1-9])?[+-]?(?=[ ]|$)',
             set_block_scalar_indent(Punctuation.Indicator),
             'ignored-line'),
            # chomping flag followed by indentation indicator
            (r'[+-]?([1-9])?(?=[ ]|$)',
             set_block_scalar_indent(Punctuation.Indicator),
             'ignored-line'),
        ],

        # ignored and regular whitespaces in quoted scalars
        'quoted-scalar-whitespaces': [
            # leading and trailing whitespaces are ignored
            (r'^[ ]+', Text),
            (r'[ ]+$', Text),
            # line breaks are ignored
            (r'\n+', Text),
            # other whitespaces are a part of the value
            (r'[ ]+', Name.Variable),
        ],

        # single-quoted scalars
        'single-quoted-scalar': [
            # include whitespace and line break rules
            include('quoted-scalar-whitespaces'),
            # escaping of the quote character
            (r'\'\'', String.Escape),
            # regular non-whitespace characters
            (r'[^\s\']+', String),
            # the closing quote
            (r'\'', String, '#pop'),
        ],

        # double-quoted scalars
        'double-quoted-scalar': [
            # include whitespace and line break rules
            include('quoted-scalar-whitespaces'),
            # escaping of special characters
            (r'\\[0abt\tn\nvfre "\\N_LP]', String),
            # escape codes
            (r'\\(?:x[0-9A-Fa-f]{2}|u[0-9A-Fa-f]{4}|U[0-9A-Fa-f]{8})',
             String.Escape),
            # regular non-whitespace characters
            (r'[^\s"\\]+', String),
            # the closing quote
            (r'"', String, '#pop'),
        ],

        # the beginning of a new line while scanning a plain scalar
        'plain-scalar-in-block-context-new-line': [
            # empty lines
            (r'^[ ]+$', Text),
            # line breaks
            (r'\n+', Text),
            # document start and document end indicators
            (r'^(?=---|\.\.\.)', something(Name.Namespace), '#pop:3'),
            # indentation spaces (we may leave the block line state here)
            (r'^[ ]*', parse_plain_scalar_indent(Text), '#pop'),
        ],

        # a plain scalar in the block context
        'plain-scalar-in-block-context': [
            # the scalar ends with the ':' indicator
            (r'[ ]*(?=:[ ]|:$)', something(Text), '#pop'),
            # the scalar ends with whitespaces followed by a comment
            (r'[ ]+(?=#)', Text, '#pop'),
            # trailing whitespaces are ignored
            (r'[ ]+$', Text),
            # line breaks are ignored
            (r'\n+', Text, 'plain-scalar-in-block-context-new-line'),
            # other whitespaces are a part of the value
            (r'[ ]+', Literal.Scalar.Plain),
            # regular non-whitespace characters
            (r'(?::(?!\s)|[^\s:])+', Literal.Scalar.Plain),
        ],

        # a plain scalar is the flow context
        'plain-scalar-in-flow-context': [
            # the scalar ends with an indicator character
            (r'[ ]*(?=[,:?\[\]{}])', something(Text), '#pop'),
            # the scalar ends with a comment
            (r'[ ]+(?=#)', Text, '#pop'),
            # leading and trailing whitespaces are ignored
            (r'^[ ]+', Text),
            (r'[ ]+$', Text),
            # line breaks are ignored
            (r'\n+', Text),
            # other whitespaces are a part of the value
            (r'[ ]+', Name.Variable),
            # regular non-whitespace characters
            (r'[^\s,:?\[\]{}]+', Name.Variable),
        ],

    }

    def get_tokens_unprocessed(self, text=None, context=None):
        if context is None:
            context = YamlLexerContext(text, 0)
        return super().get_tokens_unprocessed(text, context)


class JsonLexer(Lexer):
    """
    For JSON data structures.

    .. versionadded:: 1.5
    """

    name = 'JSON'
    aliases = ['json', 'json-object']
    filenames = ['*.json', 'Pipfile.lock']
    mimetypes = ['application/json', 'application/json-object']

    # No validation of integers, floats, or constants is done.
    # As long as the characters are members of the following
    # sets, the token will be considered valid. For example,
    #
    #     "--1--" is parsed as an integer
    #     "1...eee" is parsed as a float
    #     "trustful" is parsed as a constant
    #
    integers = set('-0123456789')
    floats = set('.eE+')
    constants = set('truefalsenull')  # true|false|null
    hexadecimals = set('0123456789abcdefABCDEF')
    punctuations = set('{}[],')
    whitespaces = {'\u0020', '\u000a', '\u000d', '\u0009'}

    def get_tokens_unprocessed(self, text):
        """Parse JSON data."""

        in_string = False
        in_escape = False
        in_unicode_escape = 0
        in_whitespace = False
        in_constant = False
        in_number = False
        in_float = False
        in_punctuation = False

        start = 0

        # The queue is used to store data that may need to be tokenized
        # differently based on what follows. In particular, JSON object
        # keys are tokenized differently than string values, but cannot
        # be distinguished until punctuation is encountered outside the
        # string.
        #
        # A ":" character after the string indicates that the string is
        # an object key; any other character indicates the string is a
        # regular string value.
        #
        # The queue holds tuples that contain the following data:
        #
        #     (start_index, token_type, text)
        #
        # By default the token type of text in double quotes is
        # String.Double. The token type will be replaced if a colon
        # is encountered after the string closes.
        #
        queue = []

        for stop, character in enumerate(text):
            if in_string:
                if in_unicode_escape:
                    if character in self.hexadecimals:
                        in_unicode_escape -= 1
                        if not in_unicode_escape:
                            in_escape = False
                    else:
                        in_unicode_escape = 0
                        in_escape = False

                elif in_escape:
                    if character == 'u':
                        in_unicode_escape = 4
                    else:
                        in_escape = False

                elif character == '\\':
                    in_escape = True

                elif character == '"':
                    queue.append((start, String.Double, text[start:stop + 1]))
                    in_string = False
                    in_escape = False
                    in_unicode_escape = 0

                continue

            elif in_whitespace:
                if character in self.whitespaces:
                    continue

                if queue:
                    queue.append((start, Text, text[start:stop]))
                else:
                    yield start, Text, text[start:stop]
                in_whitespace = False
                # Fall through so the new character can be evaluated.

            elif in_constant:
                if character in self.constants:
                    continue

                yield start, Keyword.Constant, text[start:stop]
                in_constant = False
                # Fall through so the new character can be evaluated.

            elif in_number:
                if character in self.integers:
                    continue
                elif character in self.floats:
                    in_float = True
                    continue

                if in_float:
                    yield start, Number.Float, text[start:stop]
                else:
                    yield start, Number.Integer, text[start:stop]
                in_number = False
                in_float = False
                # Fall through so the new character can be evaluated.

            elif in_punctuation:
                if character in self.punctuations:
                    continue

                yield start, Punctuation, text[start:stop]
                in_punctuation = False
                # Fall through so the new character can be evaluated.

            start = stop

            if character == '"':
                in_string = True

            elif character in self.whitespaces:
                in_whitespace = True

            elif character in {'f', 'n', 't'}:  # The first letters of true|false|null
                # Exhaust the queue. Accept the existing token types.
                yield from queue
                queue.clear()

                in_constant = True

            elif character in self.integers:
                # Exhaust the queue. Accept the existing token types.
                yield from queue
                queue.clear()

                in_number = True

            elif character == ':':
                # Yield from the queue. Replace string token types.
                for _start, _token, _text in queue:
                    if _token is Text:
                        yield _start, _token, _text
                    elif _token is String.Double:
                        yield _start, Name.Tag, _text
                    else:
                        yield _start, Error, _text
                queue.clear()

                in_punctuation = True

            elif character in self.punctuations:
                # Exhaust the queue. Accept the existing token types.
                yield from queue
                queue.clear()

                in_punctuation = True

            else:
                # Exhaust the queue. Accept the existing token types.
                yield from queue
                queue.clear()

                yield start, Error, character

        # Yield any remaining text.
        yield from queue
        if in_string:
            yield start, Error, text[start:]
        elif in_float:
            yield start, Number.Float, text[start:]
        elif in_number:
            yield start, Number.Integer, text[start:]
        elif in_constant:
            yield start, Keyword.Constant, text[start:]
        elif in_whitespace:
            yield start, Text, text[start:]
        elif in_punctuation:
            yield start, Punctuation, text[start:]


class JsonBareObjectLexer(JsonLexer):
    """
    For JSON data structures (with missing object curly braces).

    .. versionadded:: 2.2

    .. deprecated:: 2.8.0

       Behaves the same as `JsonLexer` now.
    """

    name = 'JSONBareObject'
    aliases = []
    filenames = []
    mimetypes = []


class JsonLdLexer(JsonLexer):
    """
    For `JSON-LD <https://json-ld.org/>`_ linked data.

    .. versionadded:: 2.0
    """

    name = 'JSON-LD'
    aliases = ['jsonld', 'json-ld']
    filenames = ['*.jsonld']
    mimetypes = ['application/ld+json']

    json_ld_keywords = {
        '"@%s"' % keyword
        for keyword in (
            'base',
            'container',
            'context',
            'direction',
            'graph',
            'id',
            'import',
            'included',
            'index',
            'json',
            'language',
            'list',
            'nest',
            'none',
            'prefix',
            'propagate',
            'protected',
            'reverse',
            'set',
            'type',
            'value',
            'version',
            'vocab',
        )
    }

    def get_tokens_unprocessed(self, text):
        for start, token, value in super().get_tokens_unprocessed(text):
            if token is Name.Tag and value in self.json_ld_keywords:
                yield start, Name.Decorator, value
            else:
                yield start, token, value
