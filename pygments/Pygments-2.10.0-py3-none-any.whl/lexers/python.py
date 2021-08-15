"""
    pygments.lexers.python
    ~~~~~~~~~~~~~~~~~~~~~~

    Lexers for Python and related languages.

    :copyright: Copyright 2006-2021 by the Pygments team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

import re

from pygments.lexer import Lexer, RegexLexer, include, bygroups, using, \
    default, words, combined, do_insertions
from pygments.util import get_bool_opt, shebang_matches
from pygments.token import Text, Comment, Operator, Keyword, Name, String, \
    Number, Punctuation, Generic, Other, Error
from pygments import unistring as uni

__all__ = ['PythonLexer', 'PythonConsoleLexer', 'PythonTracebackLexer',
           'Python2Lexer', 'Python2TracebackLexer',
           'CythonLexer', 'DgLexer', 'NumPyLexer']

line_re = re.compile('.*?\n')


class PythonLexer(RegexLexer):
    """
    For `Python <http://www.python.org>`_ source code (version 3.x).

    .. versionadded:: 0.10

    .. versionchanged:: 2.5
       This is now the default ``PythonLexer``.  It is still available as the
       alias ``Python3Lexer``.
    """

    name = 'Python'
    aliases = ['python', 'py', 'sage', 'python3', 'py3']
    filenames = [
        '*.py',
        '*.pyw',
        # Jython
        '*.jy',
        # Sage
        '*.sage',
        # SCons
        '*.sc',
        'SConstruct',
        'SConscript',
        # Skylark/Starlark (used by Bazel, Buck, and Pants)
        '*.bzl',
        'BUCK',
        'BUILD',
        'BUILD.bazel',
        'WORKSPACE',
        # Twisted Application infrastructure
        '*.tac',
    ]
    mimetypes = ['text/x-python', 'application/x-python',
                 'text/x-python3', 'application/x-python3']

    flags = re.MULTILINE | re.UNICODE

    uni_name = "[%s][%s]*" % (uni.xid_start, uni.xid_continue)

    def innerstring_rules(ttype):
        return [
            # the old style '%s' % (...) string formatting (still valid in Py3)
            (r'%(\(\w+\))?[-#0 +]*([0-9]+|[*])?(\.([0-9]+|[*]))?'
             '[hlL]?[E-GXc-giorsaux%]', String.Interpol),
            # the new style '{}'.format(...) string formatting
            (r'\{'
             r'((\w+)((\.\w+)|(\[[^\]]+\]))*)?'  # field name
             r'(\![sra])?'                       # conversion
             r'(\:(.?[<>=\^])?[-+ ]?#?0?(\d+)?,?(\.\d+)?[E-GXb-gnosx%]?)?'
             r'\}', String.Interpol),

            # backslashes, quotes and formatting signs must be parsed one at a time
            (r'[^\\\'"%{\n]+', ttype),
            (r'[\'"\\]', ttype),
            # unhandled string formatting sign
            (r'%|(\{{1,2})', ttype)
            # newlines are an error (use "nl" state)
        ]

    def fstring_rules(ttype):
        return [
            # Assuming that a '}' is the closing brace after format specifier.
            # Sadly, this means that we won't detect syntax error. But it's
            # more important to parse correct syntax correctly, than to
            # highlight invalid syntax.
            (r'\}', String.Interpol),
            (r'\{', String.Interpol, 'expr-inside-fstring'),
            # backslashes, quotes and formatting signs must be parsed one at a time
            (r'[^\\\'"{}\n]+', ttype),
            (r'[\'"\\]', ttype),
            # newlines are an error (use "nl" state)
        ]

    tokens = {
        'root': [
            (r'\n', Text),
            (r'^(\s*)([rRuUbB]{,2})("""(?:.|\n)*?""")',
             bygroups(Text, String.Affix, String.Doc)),
            (r"^(\s*)([rRuUbB]{,2})('''(?:.|\n)*?''')",
             bygroups(Text, String.Affix, String.Doc)),
            (r'\A#!.+$', Comment.Hashbang),
            (r'#.*$', Comment.Single),
            (r'\\\n', Text),
            (r'\\', Text),
            include('keywords'),
            (r'(def)((?:\s|\\\s)+)', bygroups(Keyword, Text), 'funcname'),
            (r'(class)((?:\s|\\\s)+)', bygroups(Keyword, Text), 'classname'),
            (r'(from)((?:\s|\\\s)+)', bygroups(Keyword.Namespace, Text),
             'fromimport'),
            (r'(import)((?:\s|\\\s)+)', bygroups(Keyword.Namespace, Text),
             'import'),
            include('expr'),
        ],
        'expr': [
            # raw f-strings
            ('(?i)(rf|fr)(""")',
             bygroups(String.Affix, String.Double),
             combined('rfstringescape', 'tdqf')),
            ("(?i)(rf|fr)(''')",
             bygroups(String.Affix, String.Single),
             combined('rfstringescape', 'tsqf')),
            ('(?i)(rf|fr)(")',
             bygroups(String.Affix, String.Double),
             combined('rfstringescape', 'dqf')),
            ("(?i)(rf|fr)(')",
             bygroups(String.Affix, String.Single),
             combined('rfstringescape', 'sqf')),
            # non-raw f-strings
            ('([fF])(""")', bygroups(String.Affix, String.Double),
             combined('fstringescape', 'tdqf')),
            ("([fF])(''')", bygroups(String.Affix, String.Single),
             combined('fstringescape', 'tsqf')),
            ('([fF])(")', bygroups(String.Affix, String.Double),
             combined('fstringescape', 'dqf')),
            ("([fF])(')", bygroups(String.Affix, String.Single),
             combined('fstringescape', 'sqf')),
            # raw strings
            ('(?i)(rb|br|r)(""")',
             bygroups(String.Affix, String.Double), 'tdqs'),
            ("(?i)(rb|br|r)(''')",
             bygroups(String.Affix, String.Single), 'tsqs'),
            ('(?i)(rb|br|r)(")',
             bygroups(String.Affix, String.Double), 'dqs'),
            ("(?i)(rb|br|r)(')",
             bygroups(String.Affix, String.Single), 'sqs'),
            # non-raw strings
            ('([uUbB]?)(""")', bygroups(String.Affix, String.Double),
             combined('stringescape', 'tdqs')),
            ("([uUbB]?)(''')", bygroups(String.Affix, String.Single),
             combined('stringescape', 'tsqs')),
            ('([uUbB]?)(")', bygroups(String.Affix, String.Double),
             combined('stringescape', 'dqs')),
            ("([uUbB]?)(')", bygroups(String.Affix, String.Single),
             combined('stringescape', 'sqs')),
            (r'[^\S\n]+', Text),
            include('numbers'),
            (r'!=|==|<<|>>|:=|[-~+/*%=<>&^|.]', Operator),
            (r'[]{}:(),;[]', Punctuation),
            (r'(in|is|and|or|not)\b', Operator.Word),
            include('expr-keywords'),
            include('builtins'),
            include('magicfuncs'),
            include('magicvars'),
            include('name'),
        ],
        'expr-inside-fstring': [
            (r'[{([]', Punctuation, 'expr-inside-fstring-inner'),
            # without format specifier
            (r'(=\s*)?'         # debug (https://bugs.python.org/issue36817)
             r'(\![sraf])?'     # conversion
             r'\}', String.Interpol, '#pop'),
            # with format specifier
            # we'll catch the remaining '}' in the outer scope
            (r'(=\s*)?'         # debug (https://bugs.python.org/issue36817)
             r'(\![sraf])?'     # conversion
             r':', String.Interpol, '#pop'),
            (r'\s+', Text),  # allow new lines
            include('expr'),
        ],
        'expr-inside-fstring-inner': [
            (r'[{([]', Punctuation, 'expr-inside-fstring-inner'),
            (r'[])}]', Punctuation, '#pop'),
            (r'\s+', Text),  # allow new lines
            include('expr'),
        ],
        'expr-keywords': [
            # Based on https://docs.python.org/3/reference/expressions.html
            (words((
                'async for', 'await', 'else', 'for', 'if', 'lambda',
                'yield', 'yield from'), suffix=r'\b'),
             Keyword),
            (words(('True', 'False', 'None'), suffix=r'\b'), Keyword.Constant),
        ],
        'keywords': [
            (words((
                'assert', 'async', 'await', 'break', 'continue', 'del', 'elif',
                'else', 'except', 'finally', 'for', 'global', 'if', 'lambda',
                'pass', 'raise', 'nonlocal', 'return', 'try', 'while', 'yield',
                'yield from', 'as', 'with'), suffix=r'\b'),
             Keyword),
            (words(('True', 'False', 'None'), suffix=r'\b'), Keyword.Constant),
        ],
        'builtins': [
            (words((
                '__import__', 'abs', 'all', 'any', 'bin', 'bool', 'bytearray',
                'bytes', 'chr', 'classmethod', 'compile', 'complex',
                'delattr', 'dict', 'dir', 'divmod', 'enumerate', 'eval', 'filter',
                'float', 'format', 'frozenset', 'getattr', 'globals', 'hasattr',
                'hash', 'hex', 'id', 'input', 'int', 'isinstance', 'issubclass',
                'iter', 'len', 'list', 'locals', 'map', 'max', 'memoryview',
                'min', 'next', 'object', 'oct', 'open', 'ord', 'pow', 'print',
                'property', 'range', 'repr', 'reversed', 'round', 'set', 'setattr',
                'slice', 'sorted', 'staticmethod', 'str', 'sum', 'super', 'tuple',
                'type', 'vars', 'zip'), prefix=r'(?<!\.)', suffix=r'\b'),
             Name.Builtin),
            (r'(?<!\.)(self|Ellipsis|NotImplemented|cls)\b', Name.Builtin.Pseudo),
            (words((
                'ArithmeticError', 'AssertionError', 'AttributeError',
                'BaseException', 'BufferError', 'BytesWarning', 'DeprecationWarning',
                'EOFError', 'EnvironmentError', 'Exception', 'FloatingPointError',
                'FutureWarning', 'GeneratorExit', 'IOError', 'ImportError',
                'ImportWarning', 'IndentationError', 'IndexError', 'KeyError',
                'KeyboardInterrupt', 'LookupError', 'MemoryError', 'NameError',
                'NotImplementedError', 'OSError', 'OverflowError',
                'PendingDeprecationWarning', 'ReferenceError', 'ResourceWarning',
                'RuntimeError', 'RuntimeWarning', 'StopIteration',
                'SyntaxError', 'SyntaxWarning', 'SystemError', 'SystemExit',
                'TabError', 'TypeError', 'UnboundLocalError', 'UnicodeDecodeError',
                'UnicodeEncodeError', 'UnicodeError', 'UnicodeTranslateError',
                'UnicodeWarning', 'UserWarning', 'ValueError', 'VMSError',
                'Warning', 'WindowsError', 'ZeroDivisionError',
                # new builtin exceptions from PEP 3151
                'BlockingIOError', 'ChildProcessError', 'ConnectionError',
                'BrokenPipeError', 'ConnectionAbortedError', 'ConnectionRefusedError',
                'ConnectionResetError', 'FileExistsError', 'FileNotFoundError',
                'InterruptedError', 'IsADirectoryError', 'NotADirectoryError',
                'PermissionError', 'ProcessLookupError', 'TimeoutError',
                # others new in Python 3
                'StopAsyncIteration', 'ModuleNotFoundError', 'RecursionError'),
                prefix=r'(?<!\.)', suffix=r'\b'),
             Name.Exception),
        ],
        'magicfuncs': [
            (words((
                '__abs__', '__add__', '__aenter__', '__aexit__', '__aiter__',
                '__and__', '__anext__', '__await__', '__bool__', '__bytes__',
                '__call__', '__complex__', '__contains__', '__del__', '__delattr__',
                '__delete__', '__delitem__', '__dir__', '__divmod__', '__enter__',
                '__eq__', '__exit__', '__float__', '__floordiv__', '__format__',
                '__ge__', '__get__', '__getattr__', '__getattribute__',
                '__getitem__', '__gt__', '__hash__', '__iadd__', '__iand__',
                '__ifloordiv__', '__ilshift__', '__imatmul__', '__imod__',
                '__imul__', '__index__', '__init__', '__instancecheck__',
                '__int__', '__invert__', '__ior__', '__ipow__', '__irshift__',
                '__isub__', '__iter__', '__itruediv__', '__ixor__', '__le__',
                '__len__', '__length_hint__', '__lshift__', '__lt__', '__matmul__',
                '__missing__', '__mod__', '__mul__', '__ne__', '__neg__',
                '__new__', '__next__', '__or__', '__pos__', '__pow__',
                '__prepare__', '__radd__', '__rand__', '__rdivmod__', '__repr__',
                '__reversed__', '__rfloordiv__', '__rlshift__', '__rmatmul__',
                '__rmod__', '__rmul__', '__ror__', '__round__', '__rpow__',
                '__rrshift__', '__rshift__', '__rsub__', '__rtruediv__',
                '__rxor__', '__set__', '__setattr__', '__setitem__', '__str__',
                '__sub__', '__subclasscheck__', '__truediv__',
                '__xor__'), suffix=r'\b'),
             Name.Function.Magic),
        ],
        'magicvars': [
            (words((
                '__annotations__', '__bases__', '__class__', '__closure__',
                '__code__', '__defaults__', '__dict__', '__doc__', '__file__',
                '__func__', '__globals__', '__kwdefaults__', '__module__',
                '__mro__', '__name__', '__objclass__', '__qualname__',
                '__self__', '__slots__', '__weakref__'), suffix=r'\b'),
             Name.Variable.Magic),
        ],
        'numbers': [
            (r'(\d(?:_?\d)*\.(?:\d(?:_?\d)*)?|(?:\d(?:_?\d)*)?\.\d(?:_?\d)*)'
             r'([eE][+-]?\d(?:_?\d)*)?', Number.Float),
            (r'\d(?:_?\d)*[eE][+-]?\d(?:_?\d)*j?', Number.Float),
            (r'0[oO](?:_?[0-7])+', Number.Oct),
            (r'0[bB](?:_?[01])+', Number.Bin),
            (r'0[xX](?:_?[a-fA-F0-9])+', Number.Hex),
            (r'\d(?:_?\d)*', Number.Integer),
        ],
        'name': [
            (r'@' + uni_name, Name.Decorator),
            (r'@', Operator),  # new matrix multiplication operator
            (uni_name, Name),
        ],
        'funcname': [
            include('magicfuncs'),
            (uni_name, Name.Function, '#pop'),
            default('#pop'),
        ],
        'classname': [
            (uni_name, Name.Class, '#pop'),
        ],
        'import': [
            (r'(\s+)(as)(\s+)', bygroups(Text, Keyword, Text)),
            (r'\.', Name.Namespace),
            (uni_name, Name.Namespace),
            (r'(\s*)(,)(\s*)', bygroups(Text, Operator, Text)),
            default('#pop')  # all else: go back
        ],
        'fromimport': [
            (r'(\s+)(import)\b', bygroups(Text, Keyword.Namespace), '#pop'),
            (r'\.', Name.Namespace),
            # if None occurs here, it's "raise x from None", since None can
            # never be a module name
            (r'None\b', Name.Builtin.Pseudo, '#pop'),
            (uni_name, Name.Namespace),
            default('#pop'),
        ],
        'rfstringescape': [
            (r'\{\{', String.Escape),
            (r'\}\}', String.Escape),
        ],
        'fstringescape': [
            include('rfstringescape'),
            include('stringescape'),
        ],
        'stringescape': [
            (r'\\([\\abfnrtv"\']|\n|N\{.*?\}|u[a-fA-F0-9]{4}|'
             r'U[a-fA-F0-9]{8}|x[a-fA-F0-9]{2}|[0-7]{1,3})', String.Escape)
        ],
        'fstrings-single': fstring_rules(String.Single),
        'fstrings-double': fstring_rules(String.Double),
        'strings-single': innerstring_rules(String.Single),
        'strings-double': innerstring_rules(String.Double),
        'dqf': [
            (r'"', String.Double, '#pop'),
            (r'\\\\|\\"|\\\n', String.Escape),  # included here for raw strings
            include('fstrings-double')
        ],
        'sqf': [
            (r"'", String.Single, '#pop'),
            (r"\\\\|\\'|\\\n", String.Escape),  # included here for raw strings
            include('fstrings-single')
        ],
        'dqs': [
            (r'"', String.Double, '#pop'),
            (r'\\\\|\\"|\\\n', String.Escape),  # included here for raw strings
            include('strings-double')
        ],
        'sqs': [
            (r"'", String.Single, '#pop'),
            (r"\\\\|\\'|\\\n", String.Escape),  # included here for raw strings
            include('strings-single')
        ],
        'tdqf': [
            (r'"""', String.Double, '#pop'),
            include('fstrings-double'),
            (r'\n', String.Double)
        ],
        'tsqf': [
            (r"'''", String.Single, '#pop'),
            include('fstrings-single'),
            (r'\n', String.Single)
        ],
        'tdqs': [
            (r'"""', String.Double, '#pop'),
            include('strings-double'),
            (r'\n', String.Double)
        ],
        'tsqs': [
            (r"'''", String.Single, '#pop'),
            include('strings-single'),
            (r'\n', String.Single)
        ],
    }

    def analyse_text(text):
        return shebang_matches(text, r'pythonw?(3(\.\d)?)?') or \
            'import ' in text[:1000]


Python3Lexer = PythonLexer


class Python2Lexer(RegexLexer):
    """
    For `Python 2.x <http://www.python.org>`_ source code.

    .. versionchanged:: 2.5
       This class has been renamed from ``PythonLexer``.  ``PythonLexer`` now
       refers to the Python 3 variant.  File name patterns like ``*.py`` have
       been moved to Python 3 as well.
    """

    name = 'Python 2.x'
    aliases = ['python2', 'py2']
    filenames = []  # now taken over by PythonLexer (3.x)
    mimetypes = ['text/x-python2', 'application/x-python2']

    def innerstring_rules(ttype):
        return [
            # the old style '%s' % (...) string formatting
            (r'%(\(\w+\))?[-#0 +]*([0-9]+|[*])?(\.([0-9]+|[*]))?'
             '[hlL]?[E-GXc-giorsux%]', String.Interpol),
            # backslashes, quotes and formatting signs must be parsed one at a time
            (r'[^\\\'"%\n]+', ttype),
            (r'[\'"\\]', ttype),
            # unhandled string formatting sign
            (r'%', ttype),
            # newlines are an error (use "nl" state)
        ]

    tokens = {
        'root': [
            (r'\n', Text),
            (r'^(\s*)([rRuUbB]{,2})("""(?:.|\n)*?""")',
             bygroups(Text, String.Affix, String.Doc)),
            (r"^(\s*)([rRuUbB]{,2})('''(?:.|\n)*?''')",
             bygroups(Text, String.Affix, String.Doc)),
            (r'[^\S\n]+', Text),
            (r'\A#!.+$', Comment.Hashbang),
            (r'#.*$', Comment.Single),
            (r'[]{}:(),;[]', Punctuation),
            (r'\\\n', Text),
            (r'\\', Text),
            (r'(in|is|and|or|not)\b', Operator.Word),
            (r'!=|==|<<|>>|[-~+/*%=<>&^|.]', Operator),
            include('keywords'),
            (r'(def)((?:\s|\\\s)+)', bygroups(Keyword, Text), 'funcname'),
            (r'(class)((?:\s|\\\s)+)', bygroups(Keyword, Text), 'classname'),
            (r'(from)((?:\s|\\\s)+)', bygroups(Keyword.Namespace, Text),
             'fromimport'),
            (r'(import)((?:\s|\\\s)+)', bygroups(Keyword.Namespace, Text),
             'import'),
            include('builtins'),
            include('magicfuncs'),
            include('magicvars'),
            include('backtick'),
            ('([rR]|[uUbB][rR]|[rR][uUbB])(""")',
             bygroups(String.Affix, String.Double), 'tdqs'),
            ("([rR]|[uUbB][rR]|[rR][uUbB])(''')",
             bygroups(String.Affix, String.Single), 'tsqs'),
            ('([rR]|[uUbB][rR]|[rR][uUbB])(")',
             bygroups(String.Affix, String.Double), 'dqs'),
            ("([rR]|[uUbB][rR]|[rR][uUbB])(')",
             bygroups(String.Affix, String.Single), 'sqs'),
            ('([uUbB]?)(""")', bygroups(String.Affix, String.Double),
             combined('stringescape', 'tdqs')),
            ("([uUbB]?)(''')", bygroups(String.Affix, String.Single),
             combined('stringescape', 'tsqs')),
            ('([uUbB]?)(")', bygroups(String.Affix, String.Double),
             combined('stringescape', 'dqs')),
            ("([uUbB]?)(')", bygroups(String.Affix, String.Single),
             combined('stringescape', 'sqs')),
            include('name'),
            include('numbers'),
        ],
        'keywords': [
            (words((
                'assert', 'break', 'continue', 'del', 'elif', 'else', 'except',
                'exec', 'finally', 'for', 'global', 'if', 'lambda', 'pass',
                'print', 'raise', 'return', 'try', 'while', 'yield',
                'yield from', 'as', 'with'), suffix=r'\b'),
             Keyword),
        ],
        'builtins': [
            (words((
                '__import__', 'abs', 'all', 'any', 'apply', 'basestring', 'bin',
                'bool', 'buffer', 'bytearray', 'bytes', 'callable', 'chr', 'classmethod',
                'cmp', 'coerce', 'compile', 'complex', 'delattr', 'dict', 'dir', 'divmod',
                'enumerate', 'eval', 'execfile', 'exit', 'file', 'filter', 'float',
                'frozenset', 'getattr', 'globals', 'hasattr', 'hash', 'hex', 'id',
                'input', 'int', 'intern', 'isinstance', 'issubclass', 'iter', 'len',
                'list', 'locals', 'long', 'map', 'max', 'min', 'next', 'object',
                'oct', 'open', 'ord', 'pow', 'property', 'range', 'raw_input', 'reduce',
                'reload', 'repr', 'reversed', 'round', 'set', 'setattr', 'slice',
                'sorted', 'staticmethod', 'str', 'sum', 'super', 'tuple', 'type',
                'unichr', 'unicode', 'vars', 'xrange', 'zip'),
                prefix=r'(?<!\.)', suffix=r'\b'),
             Name.Builtin),
            (r'(?<!\.)(self|None|Ellipsis|NotImplemented|False|True|cls'
             r')\b', Name.Builtin.Pseudo),
            (words((
                'ArithmeticError', 'AssertionError', 'AttributeError',
                'BaseException', 'DeprecationWarning', 'EOFError', 'EnvironmentError',
                'Exception', 'FloatingPointError', 'FutureWarning', 'GeneratorExit',
                'IOError', 'ImportError', 'ImportWarning', 'IndentationError',
                'IndexError', 'KeyError', 'KeyboardInterrupt', 'LookupError',
                'MemoryError', 'NameError',
                'NotImplementedError', 'OSError', 'OverflowError', 'OverflowWarning',
                'PendingDeprecationWarning', 'ReferenceError',
                'RuntimeError', 'RuntimeWarning', 'StandardError', 'StopIteration',
                'SyntaxError', 'SyntaxWarning', 'SystemError', 'SystemExit',
                'TabError', 'TypeError', 'UnboundLocalError', 'UnicodeDecodeError',
                'UnicodeEncodeError', 'UnicodeError', 'UnicodeTranslateError',
                'UnicodeWarning', 'UserWarning', 'ValueError', 'VMSError', 'Warning',
                'WindowsError', 'ZeroDivisionError'), prefix=r'(?<!\.)', suffix=r'\b'),
             Name.Exception),
        ],
        'magicfuncs': [
            (words((
                '__abs__', '__add__', '__and__', '__call__', '__cmp__', '__coerce__',
                '__complex__', '__contains__', '__del__', '__delattr__', '__delete__',
                '__delitem__', '__delslice__', '__div__', '__divmod__', '__enter__',
                '__eq__', '__exit__', '__float__', '__floordiv__', '__ge__', '__get__',
                '__getattr__', '__getattribute__', '__getitem__', '__getslice__', '__gt__',
                '__hash__', '__hex__', '__iadd__', '__iand__', '__idiv__', '__ifloordiv__',
                '__ilshift__', '__imod__', '__imul__', '__index__', '__init__',
                '__instancecheck__', '__int__', '__invert__', '__iop__', '__ior__',
                '__ipow__', '__irshift__', '__isub__', '__iter__', '__itruediv__',
                '__ixor__', '__le__', '__len__', '__long__', '__lshift__', '__lt__',
                '__missing__', '__mod__', '__mul__', '__ne__', '__neg__', '__new__',
                '__nonzero__', '__oct__', '__op__', '__or__', '__pos__', '__pow__',
                '__radd__', '__rand__', '__rcmp__', '__rdiv__', '__rdivmod__', '__repr__',
                '__reversed__', '__rfloordiv__', '__rlshift__', '__rmod__', '__rmul__',
                '__rop__', '__ror__', '__rpow__', '__rrshift__', '__rshift__', '__rsub__',
                '__rtruediv__', '__rxor__', '__set__', '__setattr__', '__setitem__',
                '__setslice__', '__str__', '__sub__', '__subclasscheck__', '__truediv__',
                '__unicode__', '__xor__'), suffix=r'\b'),
             Name.Function.Magic),
        ],
        'magicvars': [
            (words((
                '__bases__', '__class__', '__closure__', '__code__', '__defaults__',
                '__dict__', '__doc__', '__file__', '__func__', '__globals__',
                '__metaclass__', '__module__', '__mro__', '__name__', '__self__',
                '__slots__', '__weakref__'),
                suffix=r'\b'),
             Name.Variable.Magic),
        ],
        'numbers': [
            (r'(\d+\.\d*|\d*\.\d+)([eE][+-]?[0-9]+)?j?', Number.Float),
            (r'\d+[eE][+-]?[0-9]+j?', Number.Float),
            (r'0[0-7]+j?', Number.Oct),
            (r'0[bB][01]+', Number.Bin),
            (r'0[xX][a-fA-F0-9]+', Number.Hex),
            (r'\d+L', Number.Integer.Long),
            (r'\d+j?', Number.Integer)
        ],
        'backtick': [
            ('`.*?`', String.Backtick),
        ],
        'name': [
            (r'@[\w.]+', Name.Decorator),
            (r'[a-zA-Z_]\w*', Name),
        ],
        'funcname': [
            include('magicfuncs'),
            (r'[a-zA-Z_]\w*', Name.Function, '#pop'),
            default('#pop'),
        ],
        'classname': [
            (r'[a-zA-Z_]\w*', Name.Class, '#pop')
        ],
        'import': [
            (r'(?:[ \t]|\\\n)+', Text),
            (r'as\b', Keyword.Namespace),
            (r',', Operator),
            (r'[a-zA-Z_][\w.]*', Name.Namespace),
            default('#pop')  # all else: go back
        ],
        'fromimport': [
            (r'(?:[ \t]|\\\n)+', Text),
            (r'import\b', Keyword.Namespace, '#pop'),
            # if None occurs here, it's "raise x from None", since None can
            # never be a module name
            (r'None\b', Name.Builtin.Pseudo, '#pop'),
            # sadly, in "raise x from y" y will be highlighted as namespace too
            (r'[a-zA-Z_.][\w.]*', Name.Namespace),
            # anything else here also means "raise x from y" and is therefore
            # not an error
            default('#pop'),
        ],
        'stringescape': [
            (r'\\([\\abfnrtv"\']|\n|N\{.*?\}|u[a-fA-F0-9]{4}|'
             r'U[a-fA-F0-9]{8}|x[a-fA-F0-9]{2}|[0-7]{1,3})', String.Escape)
        ],
        'strings-single': innerstring_rules(String.Single),
        'strings-double': innerstring_rules(String.Double),
        'dqs': [
            (r'"', String.Double, '#pop'),
            (r'\\\\|\\"|\\\n', String.Escape),  # included here for raw strings
            include('strings-double')
        ],
        'sqs': [
            (r"'", String.Single, '#pop'),
            (r"\\\\|\\'|\\\n", String.Escape),  # included here for raw strings
            include('strings-single')
        ],
        'tdqs': [
            (r'"""', String.Double, '#pop'),
            include('strings-double'),
            (r'\n', String.Double)
        ],
        'tsqs': [
            (r"'''", String.Single, '#pop'),
            include('strings-single'),
            (r'\n', String.Single)
        ],
    }

    def analyse_text(text):
        return shebang_matches(text, r'pythonw?2(\.\d)?')


class PythonConsoleLexer(Lexer):
    """
    For Python console output or doctests, such as:

    .. sourcecode:: pycon

        >>> a = 'foo'
        >>> print a
        foo
        >>> 1 / 0
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
        ZeroDivisionError: integer division or modulo by zero

    Additional options:

    `python3`
        Use Python 3 lexer for code.  Default is ``True``.

        .. versionadded:: 1.0
        .. versionchanged:: 2.5
           Now defaults to ``True``.
    """
    name = 'Python console session'
    aliases = ['pycon']
    mimetypes = ['text/x-python-doctest']

    def __init__(self, **options):
        self.python3 = get_bool_opt(options, 'python3', True)
        Lexer.__init__(self, **options)

    def get_tokens_unprocessed(self, text):
        if self.python3:
            pylexer = PythonLexer(**self.options)
            tblexer = PythonTracebackLexer(**self.options)
        else:
            pylexer = Python2Lexer(**self.options)
            tblexer = Python2TracebackLexer(**self.options)

        curcode = ''
        insertions = []
        curtb = ''
        tbindex = 0
        tb = 0
        for match in line_re.finditer(text):
            line = match.group()
            if line.startswith('>>> ') or line.startswith('... '):
                tb = 0
                insertions.append((len(curcode),
                                   [(0, Generic.Prompt, line[:4])]))
                curcode += line[4:]
            elif line.rstrip() == '...' and not tb:
                # only a new >>> prompt can end an exception block
                # otherwise an ellipsis in place of the traceback frames
                # will be mishandled
                insertions.append((len(curcode),
                                   [(0, Generic.Prompt, '...')]))
                curcode += line[3:]
            else:
                if curcode:
                    yield from do_insertions(
                        insertions, pylexer.get_tokens_unprocessed(curcode))
                    curcode = ''
                    insertions = []
                if (line.startswith('Traceback (most recent call last):') or
                        re.match('  File "[^"]+", line \\d+\\n$', line)):
                    tb = 1
                    curtb = line
                    tbindex = match.start()
                elif line == 'KeyboardInterrupt\n':
                    yield match.start(), Name.Class, line
                elif tb:
                    curtb += line
                    if not (line.startswith(' ') or line.strip() == '...'):
                        tb = 0
                        for i, t, v in tblexer.get_tokens_unprocessed(curtb):
                            yield tbindex+i, t, v
                        curtb = ''
                else:
                    yield match.start(), Generic.Output, line
        if curcode:
            yield from do_insertions(insertions,
                                     pylexer.get_tokens_unprocessed(curcode))
        if curtb:
            for i, t, v in tblexer.get_tokens_unprocessed(curtb):
                yield tbindex+i, t, v


class PythonTracebackLexer(RegexLexer):
    """
    For Python 3.x tracebacks, with support for chained exceptions.

    .. versionadded:: 1.0

    .. versionchanged:: 2.5
       This is now the default ``PythonTracebackLexer``.  It is still available
       as the alias ``Python3TracebackLexer``.
    """

    name = 'Python Traceback'
    aliases = ['pytb', 'py3tb']
    filenames = ['*.pytb', '*.py3tb']
    mimetypes = ['text/x-python-traceback', 'text/x-python3-traceback']

    tokens = {
        'root': [
            (r'\n', Text),
            (r'^Traceback \(most recent call last\):\n', Generic.Traceback, 'intb'),
            (r'^During handling of the above exception, another '
             r'exception occurred:\n\n', Generic.Traceback),
            (r'^The above exception was the direct cause of the '
             r'following exception:\n\n', Generic.Traceback),
            (r'^(?=  File "[^"]+", line \d+)', Generic.Traceback, 'intb'),
            (r'^.*\n', Other),
        ],
        'intb': [
            (r'^(  File )("[^"]+")(, line )(\d+)(, in )(.+)(\n)',
             bygroups(Text, Name.Builtin, Text, Number, Text, Name, Text)),
            (r'^(  File )("[^"]+")(, line )(\d+)(\n)',
             bygroups(Text, Name.Builtin, Text, Number, Text)),
            (r'^(    )(.+)(\n)',
             bygroups(Text, using(PythonLexer), Text), 'markers'),
            (r'^([ \t]*)(\.\.\.)(\n)',
             bygroups(Text, Comment, Text)),  # for doctests...
            (r'^([^:]+)(: )(.+)(\n)',
             bygroups(Generic.Error, Text, Name, Text), '#pop'),
            (r'^([a-zA-Z_][\w.]*)(:?\n)',
             bygroups(Generic.Error, Text), '#pop')
        ],
        'markers': [
            # Either `PEP 657 <https://www.python.org/dev/peps/pep-0657/>`
            # error locations in Python 3.11+, or single-caret markers
            # for syntax errors before that.
            (r'^( {4,})(\^+)(\n)',
             bygroups(Text, Punctuation.Marker, Text),
             '#pop'),
            default('#pop'),
        ],
    }


Python3TracebackLexer = PythonTracebackLexer


class Python2TracebackLexer(RegexLexer):
    """
    For Python tracebacks.

    .. versionadded:: 0.7

    .. versionchanged:: 2.5
       This class has been renamed from ``PythonTracebackLexer``.
       ``PythonTracebackLexer`` now refers to the Python 3 variant.
    """

    name = 'Python 2.x Traceback'
    aliases = ['py2tb']
    filenames = ['*.py2tb']
    mimetypes = ['text/x-python2-traceback']

    tokens = {
        'root': [
            # Cover both (most recent call last) and (innermost last)
            # The optional ^C allows us to catch keyboard interrupt signals.
            (r'^(\^C)?(Traceback.*\n)',
             bygroups(Text, Generic.Traceback), 'intb'),
            # SyntaxError starts with this.
            (r'^(?=  File "[^"]+", line \d+)', Generic.Traceback, 'intb'),
            (r'^.*\n', Other),
        ],
        'intb': [
            (r'^(  File )("[^"]+")(, line )(\d+)(, in )(.+)(\n)',
             bygroups(Text, Name.Builtin, Text, Number, Text, Name, Text)),
            (r'^(  File )("[^"]+")(, line )(\d+)(\n)',
             bygroups(Text, Name.Builtin, Text, Number, Text)),
            (r'^(    )(.+)(\n)',
             bygroups(Text, using(Python2Lexer), Text), 'marker'),
            (r'^([ \t]*)(\.\.\.)(\n)',
             bygroups(Text, Comment, Text)),  # for doctests...
            (r'^([^:]+)(: )(.+)(\n)',
             bygroups(Generic.Error, Text, Name, Text), '#pop'),
            (r'^([a-zA-Z_]\w*)(:?\n)',
             bygroups(Generic.Error, Text), '#pop')
        ],
        'marker': [
            # For syntax errors.
            (r'( {4,})(\^)', bygroups(Text, Punctuation.Marker), '#pop'),
            default('#pop'),
        ],
    }


class CythonLexer(RegexLexer):
    """
    For Pyrex and `Cython <http://cython.org>`_ source code.

    .. versionadded:: 1.1
    """

    name = 'Cython'
    aliases = ['cython', 'pyx', 'pyrex']
    filenames = ['*.pyx', '*.pxd', '*.pxi']
    mimetypes = ['text/x-cython', 'application/x-cython']

    tokens = {
        'root': [
            (r'\n', Text),
            (r'^(\s*)("""(?:.|\n)*?""")', bygroups(Text, String.Doc)),
            (r"^(\s*)('''(?:.|\n)*?''')", bygroups(Text, String.Doc)),
            (r'[^\S\n]+', Text),
            (r'#.*$', Comment),
            (r'[]{}:(),;[]', Punctuation),
            (r'\\\n', Text),
            (r'\\', Text),
            (r'(in|is|and|or|not)\b', Operator.Word),
            (r'(<)([a-zA-Z0-9.?]+)(>)',
             bygroups(Punctuation, Keyword.Type, Punctuation)),
            (r'!=|==|<<|>>|[-~+/*%=<>&^|.?]', Operator),
            (r'(from)(\d+)(<=)(\s+)(<)(\d+)(:)',
             bygroups(Keyword, Number.Integer, Operator, Name, Operator,
                      Name, Punctuation)),
            include('keywords'),
            (r'(def|property)(\s+)', bygroups(Keyword, Text), 'funcname'),
            (r'(cp?def)(\s+)', bygroups(Keyword, Text), 'cdef'),
            # (should actually start a block with only cdefs)
            (r'(cdef)(:)', bygroups(Keyword, Punctuation)),
            (r'(class|struct)(\s+)', bygroups(Keyword, Text), 'classname'),
            (r'(from)(\s+)', bygroups(Keyword, Text), 'fromimport'),
            (r'(c?import)(\s+)', bygroups(Keyword, Text), 'import'),
            include('builtins'),
            include('backtick'),
            ('(?:[rR]|[uU][rR]|[rR][uU])"""', String, 'tdqs'),
            ("(?:[rR]|[uU][rR]|[rR][uU])'''", String, 'tsqs'),
            ('(?:[rR]|[uU][rR]|[rR][uU])"', String, 'dqs'),
            ("(?:[rR]|[uU][rR]|[rR][uU])'", String, 'sqs'),
            ('[uU]?"""', String, combined('stringescape', 'tdqs')),
            ("[uU]?'''", String, combined('stringescape', 'tsqs')),
            ('[uU]?"', String, combined('stringescape', 'dqs')),
            ("[uU]?'", String, combined('stringescape', 'sqs')),
            include('name'),
            include('numbers'),
        ],
        'keywords': [
            (words((
                'assert', 'async', 'await', 'break', 'by', 'continue', 'ctypedef', 'del', 'elif',
                'else', 'except', 'except?', 'exec', 'finally', 'for', 'fused', 'gil',
                'global', 'if', 'include', 'lambda', 'nogil', 'pass', 'print',
                'raise', 'return', 'try', 'while', 'yield', 'as', 'with'), suffix=r'\b'),
             Keyword),
            (r'(DEF|IF|ELIF|ELSE)\b', Comment.Preproc),
        ],
        'builtins': [
            (words((
                '__import__', 'abs', 'all', 'any', 'apply', 'basestring', 'bin', 'bint',
                'bool', 'buffer', 'bytearray', 'bytes', 'callable', 'chr',
                'classmethod', 'cmp', 'coerce', 'compile', 'complex', 'delattr',
                'dict', 'dir', 'divmod', 'enumerate', 'eval', 'execfile', 'exit',
                'file', 'filter', 'float', 'frozenset', 'getattr', 'globals',
                'hasattr', 'hash', 'hex', 'id', 'input', 'int', 'intern', 'isinstance',
                'issubclass', 'iter', 'len', 'list', 'locals', 'long', 'map', 'max',
                'min', 'next', 'object', 'oct', 'open', 'ord', 'pow', 'property', 'Py_ssize_t',
                'range', 'raw_input', 'reduce', 'reload', 'repr', 'reversed',
                'round', 'set', 'setattr', 'slice', 'sorted', 'staticmethod',
                'str', 'sum', 'super', 'tuple', 'type', 'unichr', 'unicode', 'unsigned',
                'vars', 'xrange', 'zip'), prefix=r'(?<!\.)', suffix=r'\b'),
             Name.Builtin),
            (r'(?<!\.)(self|None|Ellipsis|NotImplemented|False|True|NULL'
             r')\b', Name.Builtin.Pseudo),
            (words((
                'ArithmeticError', 'AssertionError', 'AttributeError',
                'BaseException', 'DeprecationWarning', 'EOFError', 'EnvironmentError',
                'Exception', 'FloatingPointError', 'FutureWarning', 'GeneratorExit',
                'IOError', 'ImportError', 'ImportWarning', 'IndentationError',
                'IndexError', 'KeyError', 'KeyboardInterrupt', 'LookupError',
                'MemoryError', 'NameError', 'NotImplemented', 'NotImplementedError',
                'OSError', 'OverflowError', 'OverflowWarning',
                'PendingDeprecationWarning', 'ReferenceError', 'RuntimeError',
                'RuntimeWarning', 'StandardError', 'StopIteration', 'SyntaxError',
                'SyntaxWarning', 'SystemError', 'SystemExit', 'TabError',
                'TypeError', 'UnboundLocalError', 'UnicodeDecodeError',
                'UnicodeEncodeError', 'UnicodeError', 'UnicodeTranslateError',
                'UnicodeWarning', 'UserWarning', 'ValueError', 'Warning',
                'ZeroDivisionError'), prefix=r'(?<!\.)', suffix=r'\b'),
             Name.Exception),
        ],
        'numbers': [
            (r'(\d+\.?\d*|\d*\.\d+)([eE][+-]?[0-9]+)?', Number.Float),
            (r'0\d+', Number.Oct),
            (r'0[xX][a-fA-F0-9]+', Number.Hex),
            (r'\d+L', Number.Integer.Long),
            (r'\d+', Number.Integer)
        ],
        'backtick': [
            ('`.*?`', String.Backtick),
        ],
        'name': [
            (r'@\w+', Name.Decorator),
            (r'[a-zA-Z_]\w*', Name),
        ],
        'funcname': [
            (r'[a-zA-Z_]\w*', Name.Function, '#pop')
        ],
        'cdef': [
            (r'(public|readonly|extern|api|inline)\b', Keyword.Reserved),
            (r'(struct|enum|union|class)\b', Keyword),
            (r'([a-zA-Z_]\w*)(\s*)(?=[(:#=]|$)',
             bygroups(Name.Function, Text), '#pop'),
            (r'([a-zA-Z_]\w*)(\s*)(,)',
             bygroups(Name.Function, Text, Punctuation)),
            (r'from\b', Keyword, '#pop'),
            (r'as\b', Keyword),
            (r':', Punctuation, '#pop'),
            (r'(?=["\'])', Text, '#pop'),
            (r'[a-zA-Z_]\w*', Keyword.Type),
            (r'.', Text),
        ],
        'classname': [
            (r'[a-zA-Z_]\w*', Name.Class, '#pop')
        ],
        'import': [
            (r'(\s+)(as)(\s+)', bygroups(Text, Keyword, Text)),
            (r'[a-zA-Z_][\w.]*', Name.Namespace),
            (r'(\s*)(,)(\s*)', bygroups(Text, Operator, Text)),
            default('#pop')  # all else: go back
        ],
        'fromimport': [
            (r'(\s+)(c?import)\b', bygroups(Text, Keyword), '#pop'),
            (r'[a-zA-Z_.][\w.]*', Name.Namespace),
            # ``cdef foo from "header"``, or ``for foo from 0 < i < 10``
            default('#pop'),
        ],
        'stringescape': [
            (r'\\([\\abfnrtv"\']|\n|N\{.*?\}|u[a-fA-F0-9]{4}|'
             r'U[a-fA-F0-9]{8}|x[a-fA-F0-9]{2}|[0-7]{1,3})', String.Escape)
        ],
        'strings': [
            (r'%(\([a-zA-Z0-9]+\))?[-#0 +]*([0-9]+|[*])?(\.([0-9]+|[*]))?'
             '[hlL]?[E-GXc-giorsux%]', String.Interpol),
            (r'[^\\\'"%\n]+', String),
            # quotes, percents and backslashes must be parsed one at a time
            (r'[\'"\\]', String),
            # unhandled string formatting sign
            (r'%', String)
            # newlines are an error (use "nl" state)
        ],
        'nl': [
            (r'\n', String)
        ],
        'dqs': [
            (r'"', String, '#pop'),
            (r'\\\\|\\"|\\\n', String.Escape),  # included here again for raw strings
            include('strings')
        ],
        'sqs': [
            (r"'", String, '#pop'),
            (r"\\\\|\\'|\\\n", String.Escape),  # included here again for raw strings
            include('strings')
        ],
        'tdqs': [
            (r'"""', String, '#pop'),
            include('strings'),
            include('nl')
        ],
        'tsqs': [
            (r"'''", String, '#pop'),
            include('strings'),
            include('nl')
        ],
    }


class DgLexer(RegexLexer):
    """
    Lexer for `dg <http://pyos.github.com/dg>`_,
    a functional and object-oriented programming language
    running on the CPython 3 VM.

    .. versionadded:: 1.6
    """
    name = 'dg'
    aliases = ['dg']
    filenames = ['*.dg']
    mimetypes = ['text/x-dg']

    tokens = {
        'root': [
            (r'\s+', Text),
            (r'#.*?$', Comment.Single),

            (r'(?i)0b[01]+', Number.Bin),
            (r'(?i)0o[0-7]+', Number.Oct),
            (r'(?i)0x[0-9a-f]+', Number.Hex),
            (r'(?i)[+-]?[0-9]+\.[0-9]+(e[+-]?[0-9]+)?j?', Number.Float),
            (r'(?i)[+-]?[0-9]+e[+-]?\d+j?', Number.Float),
            (r'(?i)[+-]?[0-9]+j?', Number.Integer),

            (r"(?i)(br|r?b?)'''", String, combined('stringescape', 'tsqs', 'string')),
            (r'(?i)(br|r?b?)"""', String, combined('stringescape', 'tdqs', 'string')),
            (r"(?i)(br|r?b?)'", String, combined('stringescape', 'sqs', 'string')),
            (r'(?i)(br|r?b?)"', String, combined('stringescape', 'dqs', 'string')),

            (r"`\w+'*`", Operator),
            (r'\b(and|in|is|or|where)\b', Operator.Word),
            (r'[!$%&*+\-./:<-@\\^|~;,]+', Operator),

            (words((
                'bool', 'bytearray', 'bytes', 'classmethod', 'complex', 'dict', 'dict\'',
                'float', 'frozenset', 'int', 'list', 'list\'', 'memoryview', 'object',
                'property', 'range', 'set', 'set\'', 'slice', 'staticmethod', 'str',
                'super', 'tuple', 'tuple\'', 'type'),
                   prefix=r'(?<!\.)', suffix=r'(?![\'\w])'),
             Name.Builtin),
            (words((
                '__import__', 'abs', 'all', 'any', 'bin', 'bind', 'chr', 'cmp', 'compile',
                'complex', 'delattr', 'dir', 'divmod', 'drop', 'dropwhile', 'enumerate',
                'eval', 'exhaust', 'filter', 'flip', 'foldl1?', 'format', 'fst',
                'getattr', 'globals', 'hasattr', 'hash', 'head', 'hex', 'id', 'init',
                'input', 'isinstance', 'issubclass', 'iter', 'iterate', 'last', 'len',
                'locals', 'map', 'max', 'min', 'next', 'oct', 'open', 'ord', 'pow',
                'print', 'repr', 'reversed', 'round', 'setattr', 'scanl1?', 'snd',
                'sorted', 'sum', 'tail', 'take', 'takewhile', 'vars', 'zip'),
                   prefix=r'(?<!\.)', suffix=r'(?![\'\w])'),
             Name.Builtin),
            (r"(?<!\.)(self|Ellipsis|NotImplemented|None|True|False)(?!['\w])",
             Name.Builtin.Pseudo),

            (r"(?<!\.)[A-Z]\w*(Error|Exception|Warning)'*(?!['\w])",
             Name.Exception),
            (r"(?<!\.)(Exception|GeneratorExit|KeyboardInterrupt|StopIteration|"
             r"SystemExit)(?!['\w])", Name.Exception),

            (r"(?<![\w.])(except|finally|for|if|import|not|otherwise|raise|"
             r"subclass|while|with|yield)(?!['\w])", Keyword.Reserved),

            (r"[A-Z_]+'*(?!['\w])", Name),
            (r"[A-Z]\w+'*(?!['\w])", Keyword.Type),
            (r"\w+'*", Name),

            (r'[()]', Punctuation),
            (r'.', Error),
        ],
        'stringescape': [
            (r'\\([\\abfnrtv"\']|\n|N\{.*?\}|u[a-fA-F0-9]{4}|'
             r'U[a-fA-F0-9]{8}|x[a-fA-F0-9]{2}|[0-7]{1,3})', String.Escape)
        ],
        'string': [
            (r'%(\(\w+\))?[-#0 +]*([0-9]+|[*])?(\.([0-9]+|[*]))?'
             '[hlL]?[E-GXc-giorsux%]', String.Interpol),
            (r'[^\\\'"%\n]+', String),
            # quotes, percents and backslashes must be parsed one at a time
            (r'[\'"\\]', String),
            # unhandled string formatting sign
            (r'%', String),
            (r'\n', String)
        ],
        'dqs': [
            (r'"', String, '#pop')
        ],
        'sqs': [
            (r"'", String, '#pop')
        ],
        'tdqs': [
            (r'"""', String, '#pop')
        ],
        'tsqs': [
            (r"'''", String, '#pop')
        ],
    }


class NumPyLexer(PythonLexer):
    """
    A Python lexer recognizing Numerical Python builtins.

    .. versionadded:: 0.10
    """

    name = 'NumPy'
    aliases = ['numpy']

    # override the mimetypes to not inherit them from python
    mimetypes = []
    filenames = []

    EXTRA_KEYWORDS = {
        'abs', 'absolute', 'accumulate', 'add', 'alen', 'all', 'allclose',
        'alltrue', 'alterdot', 'amax', 'amin', 'angle', 'any', 'append',
        'apply_along_axis', 'apply_over_axes', 'arange', 'arccos', 'arccosh',
        'arcsin', 'arcsinh', 'arctan', 'arctan2', 'arctanh', 'argmax', 'argmin',
        'argsort', 'argwhere', 'around', 'array', 'array2string', 'array_equal',
        'array_equiv', 'array_repr', 'array_split', 'array_str', 'arrayrange',
        'asanyarray', 'asarray', 'asarray_chkfinite', 'ascontiguousarray',
        'asfarray', 'asfortranarray', 'asmatrix', 'asscalar', 'astype',
        'atleast_1d', 'atleast_2d', 'atleast_3d', 'average', 'bartlett',
        'base_repr', 'beta', 'binary_repr', 'bincount', 'binomial',
        'bitwise_and', 'bitwise_not', 'bitwise_or', 'bitwise_xor', 'blackman',
        'bmat', 'broadcast', 'byte_bounds', 'bytes', 'byteswap', 'c_',
        'can_cast', 'ceil', 'choose', 'clip', 'column_stack', 'common_type',
        'compare_chararrays', 'compress', 'concatenate', 'conj', 'conjugate',
        'convolve', 'copy', 'corrcoef', 'correlate', 'cos', 'cosh', 'cov',
        'cross', 'cumprod', 'cumproduct', 'cumsum', 'delete', 'deprecate',
        'diag', 'diagflat', 'diagonal', 'diff', 'digitize', 'disp', 'divide',
        'dot', 'dsplit', 'dstack', 'dtype', 'dump', 'dumps', 'ediff1d', 'empty',
        'empty_like', 'equal', 'exp', 'expand_dims', 'expm1', 'extract', 'eye',
        'fabs', 'fastCopyAndTranspose', 'fft', 'fftfreq', 'fftshift', 'fill',
        'finfo', 'fix', 'flat', 'flatnonzero', 'flatten', 'fliplr', 'flipud',
        'floor', 'floor_divide', 'fmod', 'frexp', 'fromarrays', 'frombuffer',
        'fromfile', 'fromfunction', 'fromiter', 'frompyfunc', 'fromstring',
        'generic', 'get_array_wrap', 'get_include', 'get_numarray_include',
        'get_numpy_include', 'get_printoptions', 'getbuffer', 'getbufsize',
        'geterr', 'geterrcall', 'geterrobj', 'getfield', 'gradient', 'greater',
        'greater_equal', 'gumbel', 'hamming', 'hanning', 'histogram',
        'histogram2d', 'histogramdd', 'hsplit', 'hstack', 'hypot', 'i0',
        'identity', 'ifft', 'imag', 'index_exp', 'indices', 'inf', 'info',
        'inner', 'insert', 'int_asbuffer', 'interp', 'intersect1d',
        'intersect1d_nu', 'inv', 'invert', 'iscomplex', 'iscomplexobj',
        'isfinite', 'isfortran', 'isinf', 'isnan', 'isneginf', 'isposinf',
        'isreal', 'isrealobj', 'isscalar', 'issctype', 'issubclass_',
        'issubdtype', 'issubsctype', 'item', 'itemset', 'iterable', 'ix_',
        'kaiser', 'kron', 'ldexp', 'left_shift', 'less', 'less_equal', 'lexsort',
        'linspace', 'load', 'loads', 'loadtxt', 'log', 'log10', 'log1p', 'log2',
        'logical_and', 'logical_not', 'logical_or', 'logical_xor', 'logspace',
        'lstsq', 'mat', 'matrix', 'max', 'maximum', 'maximum_sctype',
        'may_share_memory', 'mean', 'median', 'meshgrid', 'mgrid', 'min',
        'minimum', 'mintypecode', 'mod', 'modf', 'msort', 'multiply', 'nan',
        'nan_to_num', 'nanargmax', 'nanargmin', 'nanmax', 'nanmin', 'nansum',
        'ndenumerate', 'ndim', 'ndindex', 'negative', 'newaxis', 'newbuffer',
        'newbyteorder', 'nonzero', 'not_equal', 'obj2sctype', 'ogrid', 'ones',
        'ones_like', 'outer', 'permutation', 'piecewise', 'pinv', 'pkgload',
        'place', 'poisson', 'poly', 'poly1d', 'polyadd', 'polyder', 'polydiv',
        'polyfit', 'polyint', 'polymul', 'polysub', 'polyval', 'power', 'prod',
        'product', 'ptp', 'put', 'putmask', 'r_', 'randint', 'random_integers',
        'random_sample', 'ranf', 'rank', 'ravel', 'real', 'real_if_close',
        'recarray', 'reciprocal', 'reduce', 'remainder', 'repeat', 'require',
        'reshape', 'resize', 'restoredot', 'right_shift', 'rint', 'roll',
        'rollaxis', 'roots', 'rot90', 'round', 'round_', 'row_stack', 's_',
        'sample', 'savetxt', 'sctype2char', 'searchsorted', 'seed', 'select',
        'set_numeric_ops', 'set_printoptions', 'set_string_function',
        'setbufsize', 'setdiff1d', 'seterr', 'seterrcall', 'seterrobj',
        'setfield', 'setflags', 'setmember1d', 'setxor1d', 'shape',
        'show_config', 'shuffle', 'sign', 'signbit', 'sin', 'sinc', 'sinh',
        'size', 'slice', 'solve', 'sometrue', 'sort', 'sort_complex', 'source',
        'split', 'sqrt', 'square', 'squeeze', 'standard_normal', 'std',
        'subtract', 'sum', 'svd', 'swapaxes', 'take', 'tan', 'tanh', 'tensordot',
        'test', 'tile', 'tofile', 'tolist', 'tostring', 'trace', 'transpose',
        'trapz', 'tri', 'tril', 'trim_zeros', 'triu', 'true_divide', 'typeDict',
        'typename', 'uniform', 'union1d', 'unique', 'unique1d', 'unravel_index',
        'unwrap', 'vander', 'var', 'vdot', 'vectorize', 'view', 'vonmises',
        'vsplit', 'vstack', 'weibull', 'where', 'who', 'zeros', 'zeros_like'
    }

    def get_tokens_unprocessed(self, text):
        for index, token, value in \
                PythonLexer.get_tokens_unprocessed(self, text):
            if token is Name and value in self.EXTRA_KEYWORDS:
                yield index, Keyword.Pseudo, value
            else:
                yield index, token, value

    def analyse_text(text):
        ltext = text[:1000]
        return (shebang_matches(text, r'pythonw?(3(\.\d)?)?') or
                'import ' in ltext) \
            and ('import numpy' in ltext or 'from numpy import' in ltext)
