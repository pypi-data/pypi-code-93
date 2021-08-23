"""Exceptions for the error class
"""

class JsonViewerException(Exception):
    pass

class MissingFieldError(Exception):
    """Error for a missing field
    """
    def __init__(self, field):
        self.field = field 
        self.message = f"Document is missing field! Check that the field {field} is present"
        super().__init__(self.message)
