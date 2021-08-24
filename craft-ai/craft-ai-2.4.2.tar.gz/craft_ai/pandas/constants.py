class MissingValue(object):
    def __str__(self):
        return "MISSING"


class OptionalValue(object):
    def __str__(self):
        return "OPTIONAL"


MISSING_VALUE = MissingValue()
OPTIONAL_VALUE = OptionalValue()
