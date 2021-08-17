
class Error(Exception):
    pass

class test_error(Error):
    # Exception raised for testing.

    def __init__(self, message):
        self.message = message

class process_error(Error):
    # Process exception without errors tolerance

    def __init__(self, message):
        self.message = message

class excecution_error(Error):
    # Fail execution on any level

    def __init__(self, message):
        self.message = message

class definition_error(Error):
    # Wrong definition of procees, steps or flow

    def __init__(self, message):
        self.message = message
