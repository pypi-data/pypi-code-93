class BranchError(Exception):
    """
    Raised on branch related API failures. See subclasses for more specific error type.
    """
    pass


class BranchAlreadyExists(BranchError):
    """
    Raised when attempted to create a new branch with a pre-existing branch name. 
    """
    pass


class MergeError(Exception):
    """
    Raised when failed to merge specified merge request.
    """
    pass


class MergeRequestError(Exception):
    """
    Raised on merge request related API failures. See subclasses for more specific error type.
    """
    pass


class UnableToAcceptMR(MergeRequestError):
    """
    Raised on failure to accept merge request because it is either it is either a Draft, Closed, Pipeline Pending Completion, or Failed while requiring Success.
    """
    pass


class MergeConflictError(MergeRequestError):
    """
    Raise on failure to accept merge request because of merge conflicts.
    """
    pass


class JobError(Exception):
    """
    Raised on job related API failures. See subclasses for more specifi error type.
    """
    pass
