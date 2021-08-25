class ParameterErrorException(Exception):
    def __init__(self, message):
        super().__init__(message)


class MethodNotAllowedErrorException(Exception):
    def __init__(self, method, url):
        super().__init__('%s method not allowed for %s' % (method, url))


class ServiceErrorException(Exception):
    def __init__(self, message):
        super().__init__(message)


class NetworkErrorException(Exception):
    def __init__(self, message):
        super().__init__(message)


class NoResourcesException(Exception):
    def __init__(self, message):
        super().__init__(message)

class ClientErrorException(Exception):
    def __init__(self, message):
        super().__init__(message)
