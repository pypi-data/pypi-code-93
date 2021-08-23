class MediaPlatformException(Exception):
    def __init__(self, message: str = None, cause: Exception = None):
        if cause:
            message = f'{message}: {type(cause).__name__}: {cause}'

        super(MediaPlatformException, self).__init__(message)
        self.cause = cause
