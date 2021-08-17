class DskException(Exception):
    """Base KB_DSK_Basic Exception"""

    pass


class QueryExistsException(DskException):
    pass


class BadArgumentException(DskException):
    pass


class BackendErrorException(DskException):
    pass


class FeatureFileExistsException(DskException):
    def __init__(self):
        Exception.__init__(
            self, "FeatureFile already exists. Use force=True to override."
        )


class PipelineOrderException(Exception):
    pass


class PipelineDataColumnsException(Exception):
    def __init__(self):
        msg = """Warning: Binary generation is currently only possible for the following sensors:
* ACCELEROMETERX
* ACCELEROMETERY
* ACCELEROMETERZ
* GYROSCOPEX
* GYROSCOPEY
* GYROSCOPEZ
If you are using these sensors but have different names, change the column
names of your data to align with the above to generate device code."""
        print(msg)


class DuplicateValueError(Exception):
    def __init__(self, message="Duplicate values used"):
        super(DuplicateValueError, self).__init__(message)
