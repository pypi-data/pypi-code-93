import json
from .testTools import Assert, BeforeAll, PrintStats, PrintTitle, Test

from limes_common.models.network import Model, SerializableTypes, provider as Provider

class TestModel(Model):
    def __init__(self, string = '', boolean = False, integer = 0) -> None:
        self.string = string
        self.boolean = boolean
        self.integer = integer

PrintTitle(__file__)

@BeforeAll
def all(env: dict):
    return env

class Inner(Model):
    def __init__(self, a: int = 0, b: str = '') -> None:
        self.a = a
        self.b = b

class Outer(Model):
    def __init__(self, x: str = '', inner: Inner = Inner()) -> None:
        self.x = x
        self.inner = inner

class TestTypesDict(SerializableTypes):
    INNER = Inner.Parse, Inner()
    OUTER = Outer.Parse, Outer()

@Test
def modelToDict(env: dict):
    string = 'asdf'
    boolean = False
    integer = 12565
    expected = """{"string": {"L_type": "<class 'str'>", "L_value": "%s"},
        "boolean": {"L_type": "<class 'bool'>", "L_value": %s},
        "integer": {"L_type": "<class 'int'>", "L_value": %s}}""" \
        % (string, str(boolean).lower(), integer)

    model = TestModel(string, boolean, integer)
    actual = json.dumps(model.ToDict())

    Assert.Equal(json.loads(actual), json.loads(expected))

@Test
def modelLoad(env: dict):
    string = 'le string'
    boolean = True
    integer = 9000
    serialized = '''{"string": {"L_type": "<class \'str\'>", "L_value": "%s"},
        "boolean": {"L_type": "<class \'bool\'>", "L_value": %s},
        "integer": {"L_type": "<class \'int\'>", "L_value": %s}}''' \
        % (string, str(boolean).lower(), integer)

    actual = TestModel.Parse(json.loads(serialized))

    Assert.Equal(actual.string, string)
    Assert.Equal(actual.boolean, boolean)
    Assert.Equal(actual.integer, integer)

@Test
def nestedSerialize(env: dict):
    a = 25
    b = 'inside!'
    inner = Inner(a, b)
    x = 'le x string'
    outer = Outer(x, inner)
    actual = json.dumps(outer.ToDict())

    expected = '''{"x": {"L_type": "<class 'str'>", "L_value": "le x string"}, 
    "inner": {"L_type": "%s", "L_value": {
        "a": {"L_type": "<class 'int'>", "L_value": 25},
        "b": {"L_type": "<class 'str'>", "L_value": "inside!"}}}}''' % (Inner)

    Assert.Equal(json.loads(actual), json.loads(expected))

@Test
def nestedComplex(env: dict):
    class Complex(Model):
        def __init__(self, lst = [], dict = {}) -> None:
            self.List = lst
            self.Dict = dict

    com = Complex([
        1, 'lst', False,
        Inner(23, 'inner-lst')
    ], {
        'TF': True,
        'inner': Inner(2, 'inner-dict')
    })
    serialized = json.dumps(com.ToDict())

    back = Complex.Parse(serialized, TestTypesDict)
    serialized2 = json.dumps(back.ToDict())
    Assert.Equal(serialized, serialized2)

@Test
def nestedLoad(env: dict):
    a = 25
    b = 'inside!'
    inner = Inner(a, b)
    x = 'le x string'
    expected = Outer(x, inner)

    serialized = '''{"x": {"L_type": "<class 'str'>", "L_value": "le x string"}, 
    "inner": {"L_type": "%s", "L_value": {
        "a": {"L_type": "<class 'int'>", "L_value": 25},
        "b": {"L_type": "<class 'str'>", "L_value": "inside!"}}}}''' % (Inner)
    
    actual_o = Outer.Parse(serialized, TestTypesDict)
    Assert.Equal(actual_o.ToDict(), expected.ToDict())

@Test
def serviceSchema(env: dict):
    x = Provider.Service('asdf', {
        'o1': {
            'i1': bool,
            'i2': int
        },
        'o2': str
    })
    y = Provider.Service.Parse(x.ToDict())

    Assert.Equal(x.Input, y.Input)

@Test
def rawDict(env: dict):
    x = Provider.Generic('test', {
        'd': {
            'a': 1,
            'b': True
        },
        'l': [
            0.3, 'a string'
        ],
        'p': 'pval'
    })
    y = Provider.Generic.Load(json.dumps(x.ToDict()))
    Assert.Equal(x.Data, y.Data)
    

PrintStats()