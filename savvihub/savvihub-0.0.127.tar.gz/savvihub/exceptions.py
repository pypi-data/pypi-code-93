class SavviHubException(BaseException):
    message = None
    exit_code = 1

    def __init__(self, message=None, exit_code=1):
        self.exit_code = exit_code
        if message:
            self.message = message


class PathException(SavviHubException):
    pass


class ArgumentException(SavviHubException):
    pass
