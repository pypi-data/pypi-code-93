class ParameterErrorException(Exception):
    def __init__(self, message):
        super().__init__(message)


class MethodNotAllowedErrorException(Exception):
    def __init__(self, message):
        super().__init__(message)


class ServiceErrorException(Exception):
    def __init__(self, message):
        super().__init__(message)


class NetworkErrorException(Exception):
    def __init__(self, message):
        super().__init__(message)
