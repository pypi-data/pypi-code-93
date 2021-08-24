class DummyProgressDialog(object):
    """
    This class is used when not running arcMap in desktop mode since the
    pythonaddins ProgressDialog will have an exception.  It has to be run
    via a with statement, so this class provides an alternate with statement
    """

    def __init__(self):
        pass

    def __enter__(self):
        return True

    def __exit__(self, *args):
        return False
