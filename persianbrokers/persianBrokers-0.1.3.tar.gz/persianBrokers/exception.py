class TokenException(BaseException):
    def __init__(self, msg=None):
        self.msg = msg

    def __str__(self):
        return f'token_exception, {self.msg or "has been raised"}'