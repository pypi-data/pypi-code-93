import os

from requests.models import Response

from limes_common.models.network.elab import Login

from .testTools import Assert, BeforeAll, PrintStats, PrintTitle, Test

from limes_common.connections import Connection
from limes_common.connections.statics import ServerConnection, ELabConnection
from limes_common.connections.ssh import SshConnection
from limes_common.models.network import ErrorModel, server
from limes_common import config

def getec(env) -> ELabConnection:
    return env['ec']
def getserv(env) -> ServerConnection:
    return env['serv']


PrintTitle(__file__)

@BeforeAll
def all(env: dict):
    env['ec'] = ELabConnection()
    env['serv'] = ServerConnection()
    return env

@Test
def elablogin(env: dict):
    ec = getec(env)
    ext = 'msl' if 'msl' in config.ELAB_URL else 'test' 
    path = '../../credentials/elab.%s' % ext
    u, p = list(line[:-1] for line in open(path, 'r').readlines()[:2])
    
    res = ec.Login(u, p)
    env['f'] = res.FirstName
    env['l'] = res.LastName
    Assert.Equal(res.Code, 200)
    if res.Token is None or res.Token == '':
        Assert.Fail()

@Test
def serverLogin(env: dict):
    ext = 'msl' if 'msl' in config.ELAB_URL else 'test' 
    path = '../../credentials/elab.%s' % ext
    tok = list(line[:-1] for line in open(path, 'r').readlines())[2]
    serv = getserv(env)
    res = serv.Send(
        server.Login.Request(tok, 'test_FN', 'test_LN'),
        server.Login.Response.Parse,
    )

    if isinstance(res, ErrorModel):
        Assert.Fail(res.Message)

    Assert.Equal(res.Success, True)

PrintStats()