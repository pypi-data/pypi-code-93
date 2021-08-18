class OutOfService(Exception):
    def __init__(self,Note:str=""):
        pass
class InternalError(Exception):
    def __init__(self,Note:str=""):
        pass
class NothingFoundError(Exception):
    def __init__(self,Note:str=""):
        pass
class DummyError(Exception):
    def __init__(self,Note:str=""):
        pass
class NotImplemented(Exception):
    def __init__(self,Note:str=""):
        pass
class NotActivated(Exception):
    def __init__(self,Note:str=""):
        pass
class InvalidAuth(Exception):
    def __init__(self,Note:str=""):
        pass
class NonExsistant(Exception):
    def __init__(self,Note:str=""):
        pass