from typing import Callable, Tuple, Type, Union


def catch_and_throw(catch: Union[Type[Exception], Tuple[Type[Exception]]],
                    throw: Type[Exception]):
    # catch the first exception(s), throw the second
    def deco(fun: Callable):
        def wrap(*args, **kwargs):
            try:
                return fun(*args, **kwargs)
            except catch:
                raise throw
        return wrap
    return deco


class JSONRPCError(Exception):
    associated_request = None
    code: int = None
    message: str = None


class ParseError(JSONRPCError):
    code = -32700
    message = 'Parse error'


class InvalidRequestError(JSONRPCError):
    code = -32600
    message = 'Invalid Request'


class MethodNotFoundError(JSONRPCError):
    code = -32601
    message = 'Method not found'


class InvalidParamsError(JSONRPCError):
    code = -32602
    message = 'Invalid params'


class InternalError(JSONRPCError):
    code = -32603
    message = 'Internal error'


