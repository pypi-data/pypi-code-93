'''
======================================================================
Error classses for carte blanche_utils validators
----------------------------------------------------------------------
'''


class ValidatorException(Exception):
    """docstring for ValidatorException"""
    def __init__(self):
        super(ValidatorException, self).__init__()


class SchemaException(ValidatorException):
    """docstring for SchemaException"""
    def __init__(self, args):
        super(SchemaException, self).__init__()
        self.title = args.get('title', 'SchemaException')
        self.exception = {
            'title': self.title,
            'detail': f'Invalid Schema: {args["exception"]}'
        }


class ValidationException(ValidatorException):
    """docstring for ValidationException"""
    def __init__(self, args):
        super(ValidationException, self).__init__()
        self.title = args.get('title', 'ValidationException')
        self.exception = {
            'title': self.title,
            'detail': f'An exception occurred during validation: {args["exception"]}'
        }
