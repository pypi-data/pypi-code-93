from savvihub.exceptions import SavviHubException


class ExitException(SavviHubException):
    """ Usage: raise ExitError('error message') """


class InvalidGitRepository(SavviHubException):
    pass


