"""
    pygments.lexers.mosel
    ~~~~~~~~~~~~~~~~~~~~~

    Lexers for the mosel language.
    http://www.fico.com/en/products/fico-xpress-optimization

    :copyright: Copyright 2006-2021 by the Pygments team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

from pygments.lexer import RegexLexer
from pygments.lexer import words
from pygments.token import Comment
from pygments.token import Keyword
from pygments.token import Name
from pygments.token import Number
from pygments.token import Operator
from pygments.token import Punctuation
from pygments.token import String
from pygments.token import Text

__all__ = ['MoselLexer']

FUNCTIONS = (
    # core functions
    '_',
    'abs',
    'arctan',
    'asproc',
    'assert',
    'bitflip',
    'bitneg',
    'bitset',
    'bitshift',
    'bittest',
    'bitval',
    'ceil',
    'cos',
    'create',
    'currentdate',
    'currenttime',
    'cutelt',
    'cutfirst',
    'cuthead',
    'cutlast',
    'cuttail',
    'datablock',
    'delcell',
    'exists',
    'exit',
    'exp',
    'exportprob',
    'fclose',
    'fflush',
    'finalize',
    'findfirst',
    'findlast',
    'floor',
    'fopen',
    'fselect',
    'fskipline',
    'fwrite',
    'fwrite_',
    'fwriteln',
    'fwriteln_',
    'getact',
    'getcoeff',
    'getcoeffs',
    'getdual',
    'getelt',
    'getfid',
    'getfirst',
    'getfname',
    'gethead',
    'getlast',
    'getobjval',
    'getparam',
    'getrcost',
    'getreadcnt',
    'getreverse',
    'getsize',
    'getslack',
    'getsol',
    'gettail',
    'gettype',
    'getvars',
    'isdynamic',
    'iseof',
    'isfinite',
    'ishidden',
    'isinf',
    'isnan',
    'isodd',
    'ln',
    'localsetparam',
    'log',
    'makesos1',
    'makesos2',
    'maxlist',
    'memoryuse',
    'minlist',
    'newmuid',
    'publish',
    'random',
    'read',
    'readln',
    'reset',
    'restoreparam',
    'reverse',
    'round',
    'setcoeff',
    'sethidden',
    'setioerr',
    'setmatherr',
    'setname',
    'setparam',
    'setrandseed',
    'setrange',
    'settype',
    'sin',
    'splithead',
    'splittail',
    'sqrt',
    'strfmt',
    'substr',
    'timestamp',
    'unpublish',
    'versionnum',
    'versionstr',
    'write',
    'write_',
    'writeln',
    'writeln_',

    # mosel exam mmxprs | sed -n -e "s/ [pf][a-z]* \([a-zA-Z0-9_]*\).*/'\1',/p" | sort -u
    'addcut',
    'addcuts',
    'addmipsol',
    'basisstability',
    'calcsolinfo',
    'clearmipdir',
    'clearmodcut',
    'command',
    'copysoltoinit',
    'crossoverlpsol',
    'defdelayedrows',
    'defsecurevecs',
    'delcuts',
    'dropcuts',
    'estimatemarginals',
    'fixglobal',
    'flushmsgq',
    'getbstat',
    'getcnlist',
    'getcplist',
    'getdualray',
    'getiis',
    'getiissense',
    'getiistype',
    'getinfcause',
    'getinfeas',
    'getlb',
    'getlct',
    'getleft',
    'getloadedlinctrs',
    'getloadedmpvars',
    'getname',
    'getprimalray',
    'getprobstat',
    'getrange',
    'getright',
    'getsensrng',
    'getsize',
    'getsol',
    'gettype',
    'getub',
    'getvars',
    'gety',
    'hasfeature',
    'implies',
    'indicator',
    'initglobal',
    'ishidden',
    'isiisvalid',
    'isintegral',
    'loadbasis',
    'loadcuts',
    'loadlpsol',
    'loadmipsol',
    'loadprob',
    'maximise',
    'maximize',
    'minimise',
    'minimize',
    'postsolve',
    'readbasis',
    'readdirs',
    'readsol',
    'refinemipsol',
    'rejectintsol',
    'repairinfeas',
    'repairinfeas_deprec',
    'resetbasis',
    'resetiis',
    'resetsol',
    'savebasis',
    'savemipsol',
    'savesol',
    'savestate',
    'selectsol',
    'setarchconsistency',
    'setbstat',
    'setcallback',
    'setcbcutoff',
    'setgndata',
    'sethidden',
    'setlb',
    'setmipdir',
    'setmodcut',
    'setsol',
    'setub',
    'setucbdata',
    'stopoptimise',
    'stopoptimize',
    'storecut',
    'storecuts',
    'unloadprob',
    'uselastbarsol',
    'writebasis',
    'writedirs',
    'writeprob',
    'writesol',
    'xor',
    'xprs_addctr',
    'xprs_addindic',

    # mosel exam mmsystem | sed -n -e "s/ [pf][a-z]* \([a-zA-Z0-9_]*\).*/'\1',/p" | sort -u
    'addmonths',
    'copytext',
    'cuttext',
    'deltext',
    'endswith',
    'erase',
    'expandpath',
    'fcopy',
    'fdelete',
    'findfiles',
    'findtext',
    'fmove',
    'formattext',
    'getasnumber',
    'getchar',
    'getcwd',
    'getdate',
    'getday',
    'getdaynum',
    'getdays',
    'getdirsep',
    'getdsoparam',
    'getendparse',
    'getenv',
    'getfsize',
    'getfstat',
    'getftime',
    'gethour',
    'getminute',
    'getmonth',
    'getmsec',
    'getoserrmsg',
    'getoserror',
    'getpathsep',
    'getqtype',
    'getsecond',
    'getsepchar',
    'getsize',
    'getstart',
    'getsucc',
    'getsysinfo',
    'getsysstat',
    'gettime',
    'gettmpdir',
    'gettrim',
    'getweekday',
    'getyear',
    'inserttext',
    'isvalid',
    'jointext',
    'makedir',
    'makepath',
    'newtar',
    'newzip',
    'nextfield',
    'openpipe',
    'parseextn',
    'parseint',
    'parsereal',
    'parsetext',
    'pastetext',
    'pathmatch',
    'pathsplit',
    'qsort',
    'quote',
    'readtextline',
    'regmatch',
    'regreplace',
    'removedir',
    'removefiles',
    'setchar',
    'setdate',
    'setday',
    'setdsoparam',
    'setendparse',
    'setenv',
    'sethour',
    'setminute',
    'setmonth',
    'setmsec',
    'setoserror',
    'setqtype',
    'setsecond',
    'setsepchar',
    'setstart',
    'setsucc',
    'settime',
    'settrim',
    'setyear',
    'sleep',
    'splittext',
    'startswith',
    'system',
    'tarlist',
    'textfmt',
    'tolower',
    'toupper',
    'trim',
    'untar',
    'unzip',
    'ziplist',

    # mosel exam mmjobs | sed -n -e "s/ [pf][a-z]* \([a-zA-Z0-9_]*\).*/'\1',/p" | sort -u
    'canceltimer',
    'clearaliases',
    'compile',
    'connect',
    'detach',
    'disconnect',
    'dropnextevent',
    'findxsrvs',
    'getaliases',
    'getannidents',
    'getannotations',
    'getbanner',
    'getclass',
    'getdsoprop',
    'getdsopropnum',
    'getexitcode',
    'getfromgid',
    'getfromid',
    'getfromuid',
    'getgid',
    'gethostalias',
    'getid',
    'getmodprop',
    'getmodpropnum',
    'getnextevent',
    'getnode',
    'getrmtid',
    'getstatus',
    'getsysinfo',
    'gettimer',
    'getuid',
    'getvalue',
    'isqueueempty',
    'load',
    'nullevent',
    'peeknextevent',
    'resetmodpar',
    'run',
    'send',
    'setcontrol',
    'setdefstream',
    'setgid',
    'sethostalias',
    'setmodpar',
    'settimer',
    'setuid',
    'setworkdir',
    'stop',
    'unload',
    'wait',
    'waitexpired',
    'waitfor',
    'waitforend',
)


class MoselLexer(RegexLexer):
    """
    For the Mosel optimization language.

    .. versionadded:: 2.6
    """
    name = 'Mosel'
    aliases = ['mosel']
    filenames = ['*.mos']

    tokens = {
        'root': [
            (r'\n', Text),
            (r'\s+', Text.Whitespace),
            (r'!.*?\n', Comment.Single),
            (r'\(!(.|\n)*?!\)', Comment.Multiline),
            (words((
                'and', 'as', 'break', 'case', 'count', 'declarations', 'do',
                'dynamic', 'elif', 'else', 'end-', 'end', 'evaluation', 'false',
                'forall', 'forward', 'from', 'function', 'hashmap', 'if',
                'imports', 'include', 'initialisations', 'initializations', 'inter',
                'max', 'min', 'model', 'namespace', 'next', 'not', 'nsgroup',
                'nssearch', 'of', 'options', 'or', 'package', 'parameters',
                'procedure', 'public', 'prod', 'record', 'repeat', 'requirements',
                'return', 'sum', 'then', 'to', 'true', 'union', 'until', 'uses',
                'version', 'while', 'with'), prefix=r'\b', suffix=r'\b'),
             Keyword.Builtin),
            (words((
                'range', 'array', 'set', 'list', 'mpvar', 'mpproblem', 'linctr',
                'nlctr', 'integer', 'string', 'real', 'boolean', 'text', 'time',
                'date', 'datetime', 'returned', 'Model', 'Mosel', 'counter',
                'xmldoc', 'is_sos1', 'is_sos2', 'is_integer', 'is_binary',
                'is_continuous', 'is_free', 'is_semcont', 'is_semint',
                'is_partint'), prefix=r'\b', suffix=r'\b'),
             Keyword.Type),
            (r'(\+|\-|\*|/|=|<=|>=|\||\^|<|>|<>|\.\.|\.|:=|::|:|in|mod|div)',
             Operator),
            (r'[()\[\]{},;]+', Punctuation),
            (words(FUNCTIONS,  prefix=r'\b', suffix=r'\b'), Name.Function),
            (r'(\d+\.(?!\.)\d*|\.(?!.)\d+)([eE][+-]?\d+)?', Number.Float),
            (r'\d+([eE][+-]?\d+)?', Number.Integer),
            (r'[+-]?Infinity', Number.Integer),
            (r'0[xX][0-9a-fA-F]+', Number),
            (r'"', String.Double, 'double_quote'),
            (r'\'', String.Single, 'single_quote'),
            (r'(\w+|(\.(?!\.)))', Text),
        ],
        'single_quote': [
            (r'\'', String.Single, '#pop'),
            (r'[^\']+', String.Single),
        ],
        'double_quote': [
            (r'(\\"|\\[0-7]{1,3}\D|\\[abfnrtv]|\\\\)', String.Escape),
            (r'\"', String.Double, '#pop'),
            (r'[^"\\]+', String.Double),
        ],
    }
