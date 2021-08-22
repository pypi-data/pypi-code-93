#!/usr/bin/env python3

import signal
import sys

from jupyter_client.consoleapp import JupyterConsoleApp
from jupyter_console.app import ZMQTerminalIPythonApp
from jupyter_console import ptshell
from pygments.lexer import RegexLexer, include, bygroups, inherit, words, \
    default
from pygments.lexers import get_lexer_by_name
from pygments.lexers.c_cpp import CppLexer
from pygments.token import Text, Comment, Operator, Keyword, Name, String, \
    Number, Punctuation, Token
from pygments.util import ClassNotFound


class Macaulay2Lexer(RegexLexer):
    name = 'Macaulay2'
    aliases = ['macaulay2', 'M2', 'm2']
    filenames = ['*.m2']
    mimetypes = ['text/x-macaulay2']

    tokens = {
        'root': [
            (words((
                'SPACE', 'and', 'break', 'catch', 'continue', 'do', 'else',
                'for', 'from', 'global', 'if', 'in', 'list', 'local', 'new',
                'not', 'of', 'or', 'return', 'shield', 'step', 'symbol',
                'then', 'throw', 'time', 'timing', 'to', 'try', 'when',
                'while'), suffix=r'\b'),
             Keyword),
            (words((
                'true', 'false', 'EulerConstant', 'Constant', 'ii', 'Constant',
                'pi', 'infinity', 'stderr', 'stdio', 'QQ', 'ZZ', 'CC', 'RR'),
                   suffix=r'\b'),
             Keyword.Constant),
            (words((
                'AbsoluteLinks', 'AfterEval', 'AfterNoPrint', 'AfterPrint',
                'Algorithm', 'Alignment', 'Ascending', 'Authors',
                'AuxiliaryFiles', 'Bareiss', 'BaseFunction', 'BaseRow',
                'BasisElementLimit', 'Bayer', 'BeforePrint', 'Binary',
                'Binomial', 'Boxes', 'CacheExampleOutput', 'CallLimit',
                'Caveat', 'Center', 'Certification', 'ChangeMatrix',
                'CheckDocumentation', 'ClosestFit', 'CodimensionLimit',
                'CoefficientRing', 'Cofactor', 'Complement',
                'CompleteIntersection', 'Configuration', 'Consequences',
                'CurrentVersion', 'Date', 'DebuggingMode', 'Decompose',
                'Degree', 'DegreeLift', 'DegreeLimit', 'DegreeMap',
                'DegreeOrder', 'DegreeRank', 'Degrees', 'Dense', 'Density',
                'Descending', 'Description', 'Dispatch', 'DivideConquer',
                'Down', 'Email', 'Encapsulate', 'EncapsulateDirectory',
                'Engine', 'Exclude', 'FileName', 'FindOne', 'First',
                'FlatMonoid', 'Flexible', 'FollowLinks', 'Format', 'GBDegrees',
                'GLex', 'GRevLex', 'Generic', 'Global', 'GlobalAssignHook',
                'GlobalReleaseHook', 'GroupLex', 'GroupRevLex',
                'HardDegreeLimit', 'Heading', 'Headline', 'Heft', 'Height',
                'Hermitian', 'Hilbert', 'HomePage', 'Homogeneous',
                'Homogeneous2', 'HorizontalSpace', 'IgnoreExampleErrors',
                'InfoDirSection', 'Inhomogeneous', 'Inputs', 'InstallPrefix',
                'Intersection', 'InverseMethod', 'Inverses', 'Iterate', 'Join',
                'KeepZeroes', 'Key', 'Left', 'LengthLimit', 'Lex', 'Limit',
                'Linear', 'LinearAlgebra', 'LoadDocumentation', 'Local',
                'LongPolynomial', 'MakeDocumentation', 'MakeInfo', 'MakeLinks',
                'MaxReductionCount', 'MaximalRank', 'MinimalGenerators',
                'MinimalMatrix', 'Minimize', 'Monomial', 'MonomialOrder',
                'MonomialSize', 'Monomials', 'NCLex', 'Name', 'NewFromMethod',
                'NewMethod', 'NewOfFromMethod', 'NewOfMethod', 'NoPrint',
                'Options', 'Order', 'Outputs', 'PackagePrefix', 'PairLimit',
                'PairsRemaining', 'Position', 'Postfix', 'Prefix',
                'PrimaryTag', 'PrimitiveElement', 'Print', 'Projective',
                'Quotient', 'Reduce', 'RemakeAllDocumentation', 'Repository',
                'RerunExamples', 'Result', 'RevLex', 'Reverse', 'Right',
                'RunExamples', 'SeeAlso', 'SeparateExec', 'SizeLimit',
                'SkewCommutative', 'Sort', 'SortStrategy', 'SourceCode',
                'SourceRing', 'Standard', 'StopBeforeComputation',
                'StopWithMinimalGenerators', 'Strategy', 'Subnodes',
                'SubringLimit', 'Sugarless', 'Syzygies', 'SyzygyLimit',
                'SyzygyMatrix', 'SyzygyRows', 'TeXmacs', 'Toric', 'TotalPairs',
                'Truncate', 'TypicalValue', 'Undo', 'Unmixed', 'Up',
                'UpdateOnly', 'UpperTriangular', 'Usage', 'UseHilbertFunction',
                'UseSyzygies', 'UserMode', 'Variable', 'VariableBaseName',
                'Variables', 'Verbose', 'Verify', 'Version', 'VerticalSpace',
                'Weights', 'WeylAlgebra', 'Wrap', 'argument', 'baseRings',
                'cache', 'dd', 'end', 'incomparable', 'indexComponents',
                'minimalPresentationMap', 'minimalPresentationMapInv', 'oo',
                'ooo', 'oooo', 'order', 'pruningMap', 'returnCode',
                'subscript', 'superscript', 'topLevelMode', 'debugLevel',
                'defaultPrecision', 'engineDebugLevel', 'errorDepth',
                'gbTrace', 'interpreterDepth', 'lineNumber', 'loadDepth',
                'maxExponent', 'minExponent', 'printWidth', 'printingAccuracy',
                'printingLeadLimit', 'printingPrecision', 'printingTimeLimit',
                'printingTrailLimit', 'recursionLimit'), suffix=r'\b'),
             Name.Variable),
            (words((
                'clearAll', 'clearOutput', 'edit', 'exit', 'help',
                'listLocalSymbols', 'clistUserSymbols', 'profileSummary',
                'quit', 'restart', 'cshowClassStructure', 'showStructure',
                'showUserStructure', 'viewHelp', 'BesselJ', 'BesselY', 'Gamma',
                'abs', 'acos', 'agm', 'alarm', 'ancestor', 'any', 'append',
                'apply', 'applyKeys', 'atEndOfFile', 'atan', 'atan2',
                'characters', 'class', 'commandInterpreter', 'concatenate',
                'cpuTime', 'csc', 'csch', 'currentDirectory', 'deepSplice',
                'difference', 'disassemble', 'drop', 'erf', 'erfc', 'exec',
                'exp', 'expm1', 'fileExists', 'flagLookup', 'floor', 'fork',
                'format', 'frames', 'getNetFile', 'getc', 'getenv', 'groupID',
                'hash', 'imaginaryPart', 'installMethod', 'instance',
                'isGlobalSymbol', 'isInfinite', 'isInputFile', 'isReady',
                'isRegularFile', 'join', 'keys', 'kill', 'locate', 'log',
                'log1p', 'lookup', 'lookupCount', 'merge', 'minimizeFilename',
                'minus', 'mkdir', 'mutable', 'openDatabase', 'openDatabaseOut',
                'openFiles', 'openOut', 'openOutAppend', 'override', 'pack',
                'pairs', 'prepend', 'printString', 'processID', 'protect',
                'readlink', 'realPart', 'realpath', 'recursionDepth',
                'relativizeFilename', 'remove', 'removeDirectory', 'scan',
                'scanPairs', 'sec', 'sech', 'select', 'separate', 'sinh',
                'size2', 'sleep', 'splice', 'sqrt', 'stack', 'substring',
                'tanh', 'times', 'toCC', 'toList', 'toRR', 'toSequence',
                'values', 'wait', 'wrap', 'xor', 'youngest', 'zeta', 'EXAMPLE',
                'gradedModuleMap', 'hold', 'html', 'hypertext', 'ideal',
                'length', 'makePackageIndex', 'mathML', 'max', 'monomialIdeal',
                'net', 'options', 'package', 'pretty', 'toExternalString',
                'toString', 'transpose', 'pseudocode', 'read', 'readDirectory',
                'regex', 'registerFinalizer', 'removeFile', 'reorganize',
                'reverse', 'run', 'sequence', 'set', 'setEcho', 'setGroupID',
                'sin', 'symlinkFile', 'take', 'tally', 'tan', 'uncurry',
                'unsequence', 'unstack', 'utf8', 'chainComplex', 'code',
                'export', 'exportMutable', 'expression', 'flatten', 'gcd',
                'gradedModule', 'info', 'intersect', 'isSorted', 'lcm',
                'maxPosition', 'commonest', 'directSum', 'examples', 'methods',
                'min', 'minPosition', 'runLengthEncode', 'tex', 'texMath',
                'undocumented', 'unique', 'vars', 'applyPairs', 'applyValues',
                'ascii', 'asin', 'clearEcho', 'collectGarbage', 'combine',
                'connectionCount', 'copy', 'cos', 'cosh', 'cot', 'coth',
                'currentLineNumber', 'currentTime', 'debugError', 'dumpdata',
                'echoOff', 'echoOn', 'eint', 'erase', 'fileLength', 'fileMode',
                'fileTime', 'firstkey', 'functionBody', 'get',
                'getGlobalSymbol', 'hashTable', 'horizontalJoin', 'identity',
                'isANumber', 'isDirectory', 'isFinite', 'isListener', 'isOpen',
                'isOutputFile', 'linkFile', 'loaddata', 'localDictionaries',
                'mergePairs', 'mingle', 'newClass', 'newNetFile', 'nextkey',
                'openIn', 'openInOut', 'openListener', 'parent', 'plus',
                'power', 'powermod', 'End', 'SYNOPSIS', 'addEndFunction',
                'addStartFunction', 'ancestors', 'applicationDirectory',
                'baseFilename', 'beginDocumentation', 'benchmark', 'columnate',
                'delete', 'demark', 'error', 'even', 'first', 'getNonUnit',
                'globalAssignFunction', 'globalAssignment', 'load',
                'makeDocumentTag', 'method', 'mod', 'monoid', 'notImplemented',
                'number', 'odd', 'on', 'pager', 'peek', 'print', 'same',
                'stashValue', 'subtable', 'synonym', 'syzygyScheme', 'table',
                'isPrimitive', 'isTable', 'last', 'lines',
                'applicationDirectorySuffix', 'applyTable', 'assert',
                'cacheValue', 'ceiling', 'centerString', 'getSymbol',
                'globalAssign', 'globalReleaseFunction', 'groebnerBasis',
                'infoHelp', 'input', 'integrate', 'inversePermutation',
                'toAbsolutePath', 'toLower', 'toUpper', 'tutorial', 'uniform',
                'monomialCurveIdeal', 'needs', 'seeParsing', 'showHtml',
                'temporaryFileName', 'userSymbols', 'vector', 'zero', 'Fano',
                'Hom', 'LUdecomposition', 'Proj', 'Spec', 'TEST', 'Wikipedia',
                'accumulate', 'acosh', 'acot', 'addHook', 'adjoint',
                'adjoint1', 'all', 'ambient', 'apropos', 'asinh', 'autoload',
                'baseName', 'between', 'binomial', 'borel', 'capture', 'char',
                'clean', 'coefficient', 'coefficientRing', 'coimage',
                'cokernel', 'columnAdd', 'columnMult', 'columnPermute',
                'columnSwap', 'commonRing', 'comodule', 'complement',
                'complete', 'components', 'compositions', 'compress', 'cone',
                'conjugate', 'content', 'contract', 'cover', 'coverMap',
                'debug', 'decompose', 'default', 'degree', 'degreeLength',
                'degrees', 'degreesMonoid', 'degreesRing', 'denominator',
                'depth', 'describe', 'diagonalMatrix', 'dictionary', 'diff',
                'dim', 'dismiss', 'divideByVariable', 'eagonNorthcott',
                'elements', 'endPackage', 'entries', 'euler', 'eulers',
                'exponents', 'findSynonyms', 'fittingIdeal', 'flip', 'fold',
                'frac', 'fraction', 'fromDual', 'gbRemove', 'gbSnapshot',
                'gcdCoefficients', 'genera', 'generateAssertions', 'generator',
                'genericMatrix', 'genericSkewMatrix', 'genericSymmetricMatrix',
                'genus', 'getChangeMatrix', 'getWWW', 'heft', 'height',
                'hilbertFunction', 'homogenize', 'homomorphism', 'httpHeaders',
                'image', 'index', 'indices', 'inducesWellDefinedMap', 'insert',
                'installAssignmentMethod', 'installHilbertFunction',
                'instances', 'inverse', 'irreducibleCharacteristicSeries',
                'isAffineRing', 'isBorel', 'isCommutative', 'isConstant',
                'isDirectSum', 'isField', 'isFreeModule', 'isHomogeneous',
                'isIdeal', 'isInjective', 'isIsomorphism', 'isModule',
                'isMonomialIdeal', 'isPolynomialRing', 'isPrime',
                'isPseudoprime', 'isQuotientModule', 'isQuotientOf',
                'isQuotientRing', 'isReal', 'isRing', 'isSkewCommutative',
                'isSquareFree', 'isSubmodule', 'isSubquotient', 'isSubset',
                'isSurjective', 'isUnit', 'isWellDefined', 'jacobian',
                'koszul', 'leadCoefficient', 'leadComponent', 'leadMonomial',
                'leadTerm', 'liftable', 'listForm', 'listSymbols', 'lngamma',
                'makeDirectory', 'match', 'member', 'memoize', 'methodOptions',
                'minimalPrimes', 'module', 'monomialSubideal', 'multidegree',
                'newCoordinateSystem', 'norm', 'nullhomotopy', 'numColumns', 'numRows',
                'numerator', 'numeric', 'numgens', 'ofClass', 'pad', 'part',
                'partition', 'partitions', 'parts', 'pdim', 'peek', 'permanents',
                'permutations', 'pfaffians', 'pivots', 'poincare', 'poincareN',
                'positions', 'precision', 'preimage', 'presentation', 'product',
                'profile', 'projectiveHilbertPolynomial', 'promote', 'pseudoRemainder',
                'quotient', 'quotientRemainder', 'rank', 'reduceHilbert', 'relations',
                'remainder', 'removeHook', 'removeLowestDimension', 'replace',
                'reshape', 'ring', 'rotate', 'round', 'rowAdd', 'rowMult',
                'rowPermute', 'rowSwap', 'runHooks', 'scanKeys', 'scanLines',
                'scanValues', 'schreyerOrder', 'searchPath', 'selectInSubring',
                'selectVariables', 'separateRegexp', 'setRandomSeed', 'setup',
                'setupEmacs', 'sheaf', 'sheafHom', 'show', 'singularLocus', 'size',
                'someTerms', 'source', 'standardForm', 'standardPairs', 'sublists',
                'submatrix', 'subquotient', 'subsets', 'substitute', 'sum', 'super',
                'support', 'switch', 'symmetricPower', 'target', 'tensorAssociativity',
                'terms', 'toDual', 'toField', 'topCoefficients', 'topComponents',
                'trace', 'truncate', 'truncateOutput', 'ultimate', 'unbag', 'use',
                'value', 'variety', 'wedgeProduct', 'weightRange', 'width', 'GF',
                'Grassmannian', 'SVD', 'Schubert', 'annihilator', 'associatedPrimes',
                'basis', 'betti', 'check', 'codim', 'coefficients', 'cohomology',
                'copyDirectory', 'copyFile', 'cotangentSheaf', 'determinant',
                'document', 'dual', 'eigenvalues', 'eigenvectors', 'extend',
                'exteriorPower', 'factor', 'fillMatrix', 'findFiles', 'flattenRing',
                'forceGB', 'gb', 'generators', 'getPackage', 'graphIdeal', 'graphRing',
                'hilbertPolynomial', 'hilbertSeries', 'homology', 'independentSets',
                'inducedMap', 'installPackage', 'kernel', 'lift', 'loadPackage', 'map',
                'markedGB', 'matrix', 'mingens', 'minimalPresentation', 'minors',
                'modulo', 'monomials', 'moveFile', 'mutableIdentity', 'mutableMatrix',
                'needsPackage', 'netList', 'newPackage', 'newRing', 'position',
                'prune', 'pushForward', 'quotient', 'radical', 'random',
                'randomMutableMatrix', 'regularity', 'res', 'resolution', 'rsort',
                'saturate', 'showTex', 'smithNormalForm', 'solve', 'sort',
                'sortColumns', 'status', 'symlinkDirectory', 'symmetricAlgebra', 'syz',
                'tangentSheaf', 'tensor', 'trim', 'uninstallPackage', 'Ext', 'HH',
                'OO', 'Tor', 'hh', 'id', 'sheafExt'), suffix=r'\b'),
             Name.Function),
            (words((
                'AffineVariety', 'Array', 'AssociativeExpression', 'BasicList',
                'BettiTally', 'Boolean', 'CacheFunction', 'CacheTable',
                'ChainComplex', 'ChainComplexMap', 'CoherentSheaf',
                'CompiledFunction', 'CompiledFunctionBody',
                'CompiledFunctionClosure', 'ComplexField', 'Constant',
                'Database', 'Descent', 'Dictionary', 'DocumentTag',
                'EngineRing', 'Expression', 'File', 'FilePosition',
                'ForestNode', 'FractionField', 'Function', 'FunctionBody',
                'FunctionClosure', 'GaloisField', 'GeneralOrderedMonoid',
                'GlobalDictionary', 'GradedModule', 'GradedModuleMap',
                'GroebnerBasis', 'GroebnerBasisOptions', 'HashTable',
                'HeaderType', 'Ideal', 'ImmutableType', 'IndeterminateNumber',
                'IndexedVariable', 'IndexedVariableTable', 'InexactField',
                'InexactFieldFamily', 'InexactNumber', 'InfiniteNumber',
                'Keyword', 'LibxmlAttribute', 'LibxmlNode', 'List',
                'LocalDictionary', 'Manipulator', 'Matrix', 'MethodFunction',
                'MethodFunctionWithOptions', 'Module', 'ModuleMap', 'Monoid',
                'MonoidElement', 'MonomialIdeal', 'MutableHashTable',
                'MutableList', 'MutableMatrix', 'Net', 'NetFile', 'Nothing',
                'Number', 'OneExpression', 'Option', 'OptionTable',
                'OrderedMonoid', 'Package', 'Partition', 'PolynomialRing',
                'ProjectiveHilbertPolynomial', 'ProjectiveVariety',
                'Pseudocode', 'QuotientRing', 'RealField', 'Resolution',
                'Ring', 'RingElement', 'RingFamily', 'RingMap',
                'ScriptedFunctor', 'SelfInitializingType', 'Sequence', 'Set',
                'SheafOfRings', 'String', 'SumOfTwists', 'Symbol', 'Tally',
                'Thing', 'Time', 'TreeNode', 'Type', 'Variety', 'Vector',
                'VirtualTally', 'VisibleList', 'WrapperType', 'ZeroExpression',
                'Holder', 'Minus', 'NonAssociativeProduct', 'Parenthesize',
                'Product', 'Sum'), suffix=r'\b'),
             Keyword.Type),
            (r'[~!%^&*+=|?:<>/@-]', Operator),
            (r'--.*$', Comment),
            (r'"', String, 'string'),
        ],
        'string': [
            (r'"', String, '#pop'),
            (r'\\([\\abfnrtv"\']|x[a-fA-F0-9]{2,4}|'
             r'u[a-fA-F0-9]{4}|U[a-fA-F0-9]{8}|[0-7]{1,3})', String.Escape),
            (r'[^\\"\n]+', String),  # all other characters
            (r'\\\n', String),  # line continuation
            (r'\\', String),  # stray backslash
        ]
    }

class SingularLexer(CppLexer):
    name = 'Singular'
    aliases = ['singular']
    filenames = ['*.sing']
    mimetypes = ['text/x-singular']

    tokens = {
        'statements': [
            (words((
                'if', 'else', 'for', 'while', 'break', 'breakpoint',
                'continue', 'export', 'exportto', 'importfrom', 'keepring',
                'load', 'quit', 'return'), suffix=r'\b'),
             Keyword),
            (words((
                'bigint', 'def', 'ideal', 'int', 'intmat', 'intvec', 'link',
                'list', 'map', 'matrix', 'module', 'number', 'package', 'poly',
                'proc', 'qring', 'resolution', 'ring', 'string', 'vector',
                'pyobject'), suffix=r'\b'),
             Keyword.Type),
            (words((
                'attrib', 'bareiss', 'betti', 'char', 'char_series', 'charstr',
                'chinrem', 'cleardenom', 'close', 'coef', 'coeffs', 'contract',
                'datetime', 'dbprint', 'defined', 'deg', 'degree', 'delete',
                'det', 'diff', 'dim', 'division', 'dump', 'eliminate', 'eval',
                'ERROR', 'example', 'execute', 'extgcd', 'facstd', 'factmodd',
                'factorize', 'farey', 'fetch', 'fglm', 'fglmquot', 'find',
                'finduni', 'fprintf', 'freemodule', 'frwalk', 'gcd', 'gen',
                'getdump', 'groebner', 'help', 'highcorner', 'hilb', 'homog',
                'hres', 'imap', 'impart', 'indepSet', 'insert',
                'interpolation', 'interred', 'intersect', 'jacob', 'janet',
                'jet', 'kbase', 'kernel', 'kill', 'killattrib', 'koszul',
                'laguerre', 'lead', 'leadcoef', 'leadexp', 'leadmonom', 'LIB',
                'lift', 'liftstd', 'listvar', 'lres', 'ludecomp', 'luinverse',
                'lusolve', 'maxideal', 'memory', 'minbase', 'minor', 'minres',
                'modulo', 'monitor', 'monomial', 'mpresmat', 'mres', 'mstd',
                'mult', 'nameof', 'names', 'ncols', 'npars', 'nres', 'nrows',
                'nvars', 'open', 'option', 'ord', 'ordstr', 'par', 'pardeg',
                'parstr', 'preimage', 'prime', 'primefactors', 'print',
                'printf', 'prune', 'qhweight', 'qrds', 'quote', 'quotient',
                'random', 'rank', 'read', 'reduce', 'regularity', 'repart',
                'res', 'reservedName', 'resultant', 'ringlist', 'rvar',
                'setring', 'simplex', 'simplify', 'size', 'slimgb', 'sortvec',
                'sqrfree', 'sprintf', 'sres', 'status', 'std', 'stdfglm',
                'stdhilb', 'subst', 'system', 'syz', 'trace', 'transpose',
                'type', 'typeof', 'univariate', 'uressolve', 'vandermonde',
                'var', 'variables', 'varstr', 'vdim', 'waitall', 'waitfirst',
                'wedge', 'weight', 'weightKB', 'write'), suffix=r'\b'),
             Name.Function),
            (r'[~!%^&*+=|?:<>/@-]', Operator),
            inherit,
        ],
    }

def get_pygments_lexer(name):
    # print(name)
    from pygments.lexers.special import TextLexer
    return TextLexer

def get_pygments_lexer(name):
    name = name.lower()
    if name == 'ipython2':
        from IPython.lib.lexers import IPythonLexer
        return IPythonLexer
    elif name == 'ipython3':
        from IPython.lib.lexers import IPython3Lexer
        return IPython3Lexer
    elif name == 'singular':
        return SingularLexer
    elif name == 'macaulay2':
        return Macaulay2Lexer
    else:
        try:
            return get_lexer_by_name(name).__class__
        except ClassNotFound:
            # warn("No lexer found for language %r. Treating as plain text." % name)
            from pygments.lexers.special import TextLexer
            return TextLexer

ptshell.get_pygments_lexer = get_pygments_lexer

class MyShell(ptshell.ZMQTerminalInteractiveShell):

    def get_prompt_tokens(self):
        return [ (Token.Prompt, '> '), ]

    def get_continuation_tokens(self, width):
        return [ (Token.Prompt, ': '), ]

    def get_out_prompt_tokens(self):
        return [ (Token.OutPrompt, ''), ]

    def show_banner(self):
        banner = self.kernel_info.get('banner', '')
        banner = banner.rstrip()
        if banner:
            print(banner, end='', flush=True)
        else:
            print("Jupyter Con", end='', flush=True)

    def interact(self, *args, **kws):
        self._some_output_printed = False
        super().interact(*args, **kws)

    def prompt_for_code(self, *args, **kws):
        self._some_output_printed = False
        return super().prompt_for_code(*args, **kws)

    def handle_iopub(self, msg_id=''):
        """Process messages on the IOPub channel
           This method consumes and processes messages on the IOPub channel,
           such as stdout, stderr, execute_result and status.
           It only displays output that is caused by this session.
        """
        while self.client.iopub_channel.msg_ready():
            sub_msg = self.client.iopub_channel.get_msg()
            msg_type = sub_msg['header']['msg_type']
            parent = sub_msg["parent_header"]

            # Update execution_count in case it changed in another session
            if msg_type == "execute_input":
                self.execution_count = int(sub_msg["content"]["execution_count"]) + 1

            if self.include_output(sub_msg):
                if msg_type == 'status':
                    self._execution_state = sub_msg["content"]["execution_state"]
                elif msg_type == 'stream':
                    if not self._some_output_printed:
                        print()
                        self._some_output_printed = True
                    if sub_msg["content"]["name"] == "stdout":
                        if self._pending_clearoutput:
                            print("\r", end="")
                            self._pending_clearoutput = False
                        print(sub_msg["content"]["text"], end="")
                        sys.stdout.flush()
                    elif sub_msg["content"]["name"] == "stderr":
                        if self._pending_clearoutput:
                            print("\r", file=sys.stderr, end="")
                            self._pending_clearoutput = False
                        print(sub_msg["content"]["text"], file=sys.stderr, end="")
                        sys.stderr.flush()

                elif msg_type == 'execute_result':
                    if not self._some_output_printed:
                        print()
                        self._some_output_printed = True
                    if self._pending_clearoutput:
                        print("\r", end="")
                        self._pending_clearoutput = False
                    self.execution_count = int(sub_msg["content"]["execution_count"])
                    if not self.from_here(sub_msg):
                        sys.stdout.write(self.other_output_prefix)
                    format_dict = sub_msg["content"]["data"]
                    self.handle_rich_data(format_dict)

                    if 'text/plain' not in format_dict:
                        continue

                    # prompt_toolkit writes the prompt at a slightly lower level,
                    # so flush streams first to ensure correct ordering.
                    sys.stdout.flush()
                    sys.stderr.flush()
                    self.print_out_prompt()
                    text_repr = format_dict['text/plain']
                    # if '\n' in text_repr:
                    #     # For multi-line results, start a new line after prompt
                    #     print()
                    print(text_repr)

                elif msg_type == 'display_data':
                    if not self._some_output_printed:
                        print()
                        self._some_output_printed = True
                    data = sub_msg["content"]["data"]
                    handled = self.handle_rich_data(data)
                    if not handled:
                        if not self.from_here(sub_msg):
                            sys.stdout.write(self.other_output_prefix)
                        # if it was an image, we handled it by now
                        if 'text/plain' in data:
                            print(data['text/plain'])

                elif msg_type == 'execute_input':
                    content = sub_msg['content']
                    if not self.from_here(sub_msg):
                        sys.stdout.write(self.other_output_prefix)
                    sys.stdout.write('In [{}]: '.format(content['execution_count']))
                    sys.stdout.write(content['code'] + '\n')

                elif msg_type == 'clear_output':
                    if sub_msg["content"]["wait"]:
                        self._pending_clearoutput = True
                    else:
                        print("\r", end="")

                elif msg_type == 'error':
                    # for frame in sub_msg["content"]["traceback"]:
                    #     print(frame, file=sys.stderr)
                    frames = sub_msg["content"]["traceback"]
                    if frames:
                        frame = frames[-1].rstrip()
                        error_lines= frame.split('\n')
                        error_line = error_lines[-1]
                        if error_line:
                            if not self._some_output_printed:
                                print()
                                self._some_output_printed = True
                            print(error_line, file=sys.stderr)


class MyApp(ZMQTerminalIPythonApp):

    def init_shell(self):
        JupyterConsoleApp.initialize(self)
        # relay sigint to kernel
        signal.signal(signal.SIGINT, self.handle_sigint)
        self.shell = MyShell.instance(
            parent=self,
            manager=self.kernel_manager,
            client=self.kernel_client,
            confirm_exit=self.confirm_exit,
        )
        self.shell.own_kernel = not self.existing

main = launch_new_instance = MyApp.launch_instance

if __name__ == '__main__':
    main()
