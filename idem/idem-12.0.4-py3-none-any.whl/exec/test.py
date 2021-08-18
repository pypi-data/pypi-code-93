__func_alias__ = {"ctx_": "ctx"}


def __init__(hub):
    hub.exec.test.ACCT = ["test"]


def ping(hub):
    return {"result": True, "ret": True}


async def aping(hub):
    return {"result": True, "ret": True}


def ctx_(hub, ctx):
    return {"result": True, "comment": None, "ret": ctx}


def fail(hub):
    raise Exception("Expected failure")


async def afail(hub):
    raise Exception("Expected failure")


def echo(hub, value):
    """
    Return the parameter passed in without changing it at all
    """
    return value


async def aecho(hub, value):
    """
    Return the parameter passed in without changing it at all
    """
    return value
