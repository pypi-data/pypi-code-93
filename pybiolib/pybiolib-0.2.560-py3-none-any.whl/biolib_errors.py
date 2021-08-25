class BioLibError(Exception):
    # pylint: disable=super-init-not-called
    def __init__(self, message):
        self.message = message
