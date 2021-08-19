class WrapperError(Exception):
    pass


class FFmpegError(WrapperError):
    pass


class YouTubeDLError(WrapperError):
    pass


class NotInCall(WrapperError):
    pass


class NotPlaying(WrapperError):
    pass


class NotPaused(WrapperError):
    pass
