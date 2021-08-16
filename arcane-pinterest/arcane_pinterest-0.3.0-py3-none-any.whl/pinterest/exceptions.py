class PinterestAccountLostAccessException(Exception):
    """ Raised when we cannot access to an account """
    pass


class PinterestAsyncReportNotReadyException(Exception):
    """ Raised when an async report is not ready yet"""
    pass
