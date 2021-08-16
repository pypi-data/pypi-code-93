class KoalaException(Exception):
    pass


class FrameworkAlreadyExistException(KoalaException):
    pass


class PluginManagerAlreadyExistException(KoalaException):
    pass


class PluginAlreadyExistException(KoalaException):
    pass


class HookManagerAlreadyExistException(KoalaException):
    pass


class HookAlreadyExistException(KoalaException):
    pass


class VariableAlreadyExistException(KoalaException):
    pass
