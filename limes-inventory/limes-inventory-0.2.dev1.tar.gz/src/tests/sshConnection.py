import json

from limes_common.connections import Criteria
from .testTools import AfterAll, Assert, BeforeAll, PrintStats, PrintTitle, Test

from limes_common.connections.ssh import SshConnection, Handler
from limes_common.models.network import Model, Primitive, SerializableTypes, provider as Provider

PrintTitle(__file__)

@BeforeAll
def all(env: dict):
    url = 'local'
    setup = [
        'cd ~/workspace/Python/Limes/package/src/',
        'conda activate limes'
    ]
    cmd = 'python -m testProvider'
    timeout = 3
    keepAlive = 10
    criteria = [
        Criteria.DATA
    ]
    con = SshConnection(url, setup, cmd, timeout, keepAlive, criteria)
    # con.AddOnResponseCallback(lambda m: print(m))
    # con.AddOnErrorCallback(lambda m: print('e>' + m))
    env['c'] = con
    return env

@Test
def checkStatus(env: dict):
    con: SshConnection = env['c']
    echo = 'test echo'
    stat = con.CheckStatus(echo)
    print(stat.Msg)
    Assert.Equal(stat.Online, True)
    Assert.Equal(stat.Echo, echo)

@Test
def getSchema(env: dict):
    con: SshConnection = env['c']
    # con.AddOnResponseCallback(lambda m: print(m))
    # con.AddOnErrorCallback(lambda m: print('e>' + m))
    s = con.GetSchema()
    for ser in s.Services:
        print(ser.Name, ser.Input, ser.Output)

    expectedServices = ['sum', 'echo', 'say hi'] 
    for i in range(len(expectedServices)):
        actual = s.Services[i].Name
        expcted = expectedServices[i]
        Assert.Equal(actual, expcted)

@Test
def testEcho(env: dict):
    con: SshConnection = env['c']
    # con.AddOnResponseCallback(lambda m: print(m))
    # con.AddOnErrorCallback(lambda m: print('e>' + m))
    sent: Primitive = {
        'message': {
            'a': 1,
            'b': True,
            'c': 'request'
        }
    }
    data = con.MakeRequest('echo', sent)
    if isinstance(data, dict):
        print(data['echo'])
        Assert.Equal(data['echo'], sent['message'])
    else:
        Assert.Fail()

@Test
def testOp(env: dict):
    con: SshConnection = env['c']
    # con.AddOnResponseCallback(lambda m: print(m))
    # con.AddOnErrorCallback(lambda m: print('e>' + m))
    sent: Primitive = {
        'values': [1, 2, 3.3]
    }
    data = con.MakeRequest('sum', sent)
    if isinstance(data, dict):
        print(data)
        Assert.Equal(data['result'], 6.3)
    else:
        Assert.Fail()

@AfterAll
def cleanup(env: dict):
    con: SshConnection = env['c']
    con.Dispose()

PrintStats()