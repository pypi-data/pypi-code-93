# -*-coding:utf-8-*-
import types
import logging

def _log(self, level, msg, args, exc_info=None, extra=None, request=None, keys=[]):
    """
    Low-level logging routine which creates a LogRecord and then calls
    all the handlers of this logger to handle the record.
    """
    if logging._srcfile:
        #IronPython doesn't track Python frames, so findCaller raises an
        #exception on some versions of IronPython. We trap it here so that
        #IronPython can use logging.
        try:
            fn, lno, func = self.findCaller()
        except ValueError:
            fn, lno, func = "(unknown file)", 0, "(unknown function)"
    else:
        fn, lno, func = "(unknown file)", 0, "(unknown function)"
    if exc_info:
        if not isinstance(exc_info, tuple):
            exc_info = sys.exc_info()
    record = self.makeRecord(self.name, level, fn, lno, msg, args, exc_info, func, extra)
    fmt_str = ""
    for key in keys:
        fmt_str = "".join(["%(", key.lower(), ")s |"])
        val = str(request.META.get(key.upper(), "None")) if request else "None"
        record.__setattr__(key.lower(), val)
    old_fmts = []
    if fmt_str:
        for handler in self.handlers:
            old_fmts.append(handler.formatter._fmt)
            handler.formatter._fmt = fmt_str + handler.formatter._fmt
    self.handle(record)
    for old_fmt in old_fmts:
        for handler in self.handlers:
            handler.formatter._fmt = old_fmt


def getLogger(name=None):
    """
    Return a logger with the specified name, creating it if necessary.

    If no name is specified, return the root logger.

    在对象logger的_log函数上打补丁，修改后的函数可以记录header信息
    """
    logger = logging.getLogger(name)
    logger._log = types.MethodType(_log, logger)
    return logger

