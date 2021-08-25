from typing import Callable, Union
from limes_common.models.basic import AbbreviatedEnum

class _bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def _cprint(col, msg):
    print(col + msg + _bcolors.ENDC)

class Assert:
    @classmethod    
    def Equal(cls, a, b):
        if str(a) != str(b):
            raise AssertionError('expected [%s] to equal [%s]' % (a, b))

    @classmethod
    def Fail(cls, msg: str = 'explicit fail'):
        raise AssertionError(msg)

    @classmethod
    def IsOfType(cls, a, b: type):
        if not isinstance(a, b):
            raise AssertionError()

    @classmethod
    def IsFalse(cls, a):
        if a:
            raise AssertionError()
    @classmethod
    def IsTrue(cls, a):
        if not a:
            raise AssertionError()
        
    @classmethod
    def IsNone(cls, a):
        if a is not None:
            raise AssertionError()
    
    @classmethod
    def IsNotNone(cls, a):
        if a is None:
            raise AssertionError()

_env = {}
_beforeAll: Callable[[dict], dict] = lambda x: x
_afterAll: Union[Callable[[dict], None], None] = None
_beforeAllCalled = False

_passed = 0
_all = 0
_file = ''

def PrintTitle(file):
    file = file.split('/')[-1][:-3]
    global _file
    _file = file
    _cprint(_bcolors.OKBLUE, '%s\n' % file)

def BeforeAll(fn: Callable[[dict], dict]) -> None:
    global _beforeAll, _beforeAllCalled
    _beforeAll = fn
    _beforeAllCalled = False
    _afterAll = None

def Test(fn: Callable[[dict], None]) -> None:
    global _env
    global _beforeAllCalled
    if not _beforeAllCalled:
        _env = _beforeAll(_env)
        _beforeAllCalled = True
    # _env = _beforeEach(_env)

    global _passed
    global _all
    print('Test: %s' % fn.__name__)
    try:
        fn(_env)
        _passed += 1
        _cprint(_bcolors.OKGREEN, 'passed!')
    except AssertionError as e:
        _cprint(_bcolors.FAIL, 'failed:\n%s' % (e))
    except Exception as x:
        _cprint(_bcolors.FAIL, 'uncaught exception:\n%s' % (x))
        # raise x
    _all += 1
    print()

def AfterAll(fn: Callable[[dict], None]) -> None:
    global _afterAll
    _afterAll = fn

def PrintStats():
    if _afterAll is not None:
        print('finishing tests for %s' % _file)
        _afterAll(_env)

    col = _bcolors.WARNING
    if _passed == _all:
        col = _bcolors.OKGREEN
    elif _passed == 0 and _all > 0:
        col = _bcolors.FAIL
    _cprint(col, '%s of %s passed' % (_passed, _all))
    print('=================================')
