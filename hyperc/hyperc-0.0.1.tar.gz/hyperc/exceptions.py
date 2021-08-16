class SchedulingError(Exception):
    pass


class SchedulingTimeout(SchedulingError):
    pass


class NoSolutionProven(SchedulingError):
    pass


class SplitterError(SchedulingError):
    pass

class NotSupportInstaceType(Exception):
    pass

class UserInterrupt(Exception):
    pass
