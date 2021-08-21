import os
from logging.handlers import RotatingFileHandler
import logging
from pathlib import Path
from cmreslogging.handlers import CMRESHandler

BASEPATH = os.getcwd()
DOCUMENT_PATH_NAME = "document"
# 文档存放路径
DOCUMENTPATH = os.path.join(BASEPATH, DOCUMENT_PATH_NAME)

SUPER_FUNC = "super_func"


def get_my_logger(file_name, file_path=DOCUMENTPATH, level='DEBUG', logger_name=__name__, **kwargs):
    """
    获取日志记录器
    :param log_path: 日志保存位置
    :param logger_name:
    :param kwargs:
    :return:
    """
    parent_path = file_path
    while not Path(file_path).exists():
        print("reset log file path!!!", file_path)
        # if not os.path.exists(file_path):
        #     os.mkdir(file_path)
        parent_path = os.path.abspath(os.path.join(parent_path, ".."))
        file_path = os.path.join(parent_path, DOCUMENT_PATH_NAME)

    file_path = os.path.join(file_path, file_name)
    print(file_path)

    logger = getLogger(file_path)
    logger.setLevel(level=getattr(logging, level.upper()))
    out_formatter = "%(levelname)s %(filename)s:%(lineno)d %(asctime)s  %(message)s"
    # 设置输出控制台
    stream_handler = logging.StreamHandler()
    stream_formatter = logging.Formatter(out_formatter, datefmt="%Y-%m-%d %H:%M:%S")
    stream_handler.setFormatter(stream_formatter)
    logger.addHandler(stream_handler)

    # 设置日志文件输出，INFO级别
    info_rt_handler = RotatingFileHandler(
        filename=file_path + ".info", mode="a", maxBytes=100 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    info_rt_handler.setLevel(level=logging.INFO)

    # 设置日志文件输出，WARNING级别
    warnig_rt_handler = RotatingFileHandler(
        filename=file_path + ".warning", mode="a", maxBytes=100 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    warnig_rt_handler.setLevel(level=logging.WARNING)

    debug_rt_handler = RotatingFileHandler(
        filename=file_path + ".debug", mode="a", maxBytes=100 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    debug_rt_handler.setLevel(level=logging.DEBUG)

    error_rt_handler = RotatingFileHandler(
        filename=file_path + ".error", mode="a", maxBytes=100 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    error_rt_handler.setLevel(level=logging.ERROR)

    critical_rt_handler = RotatingFileHandler(
        filename=file_path + ".critical", mode="a", maxBytes=100 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    critical_rt_handler.setLevel(level=logging.CRITICAL)

    # 设置打印格式
    file_rt_formatter = logging.Formatter(out_formatter, datefmt="%Y-%m-%d %H:%M:%S")

    info_rt_handler.setFormatter(file_rt_formatter)
    warnig_rt_handler.setFormatter(file_rt_formatter)
    debug_rt_handler.setFormatter(file_rt_formatter)
    error_rt_handler.setFormatter(file_rt_formatter)
    critical_rt_handler.setFormatter(file_rt_formatter)

    logger.addHandler(info_rt_handler)
    logger.addHandler(warnig_rt_handler)
    logger.addHandler(error_rt_handler)
    logger.addHandler(debug_rt_handler)
    logger.addHandler(critical_rt_handler)

    handler = CMRESHandler(
        hosts=[{"host": "192.168.111.112", "port": 9200}],
        auth_type=CMRESHandler.AuthType.NO_AUTH,
        es_index_name="python-my_tests-my-index",
    )

    logger.addHandler(handler)
    return logger


def getLogger(name=None):
    """
    Return a logger with the specified name, creating it if necessary.

    If no name is specified, return the root logger.
    """
    if name:
        MyLogger.manager.loggerClass = MyLogger
        return MyLogger.manager.getLogger(name)
    else:
        raise Exception("name is None!!!")


def logger_decorator(func):
    def wrapper(obj, msg, *args, **kwargs):
        if SUPER_FUNC in args:
            args = list(args)
            args.remove(SUPER_FUNC)
            return func(obj, msg, *args, **kwargs)

        else:
            msg = str(msg)
            msg += "  " + "  ".join([str(m) for m in args])
            return func(obj, msg, (), **kwargs)

    return wrapper


def reset_msg(msg, *args):
    try:
        if SUPER_FUNC in args:
            args = list(args)
            args.remove(SUPER_FUNC)
            return msg, args

        else:
            msg = str(msg)
            if args:
                msg += "   --   " + "   --   ".join([str(m) for m in args])
            return msg, ()
    except Exception as e:
        return msg, args


class LoggerTemplate(logging.Logger):
    def debug(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'DEBUG'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.debug("Houston, we have a %s", "thorny problem", exc_info=1)
        """
        msg, args = reset_msg(msg, *args)
        if self.isEnabledFor(logging.DEBUG):
            self._log(logging.DEBUG, msg, args, **kwargs)

    def info(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'INFO'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.info("Houston, we have a %s", "interesting problem", exc_info=1)
        """
        msg, args = reset_msg(msg, *args)
        if self.isEnabledFor(logging.INFO):
            self._log(logging.INFO, msg, args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'WARNING'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.warning("Houston, we have a %s", "bit of a problem", exc_info=1)
        """

        msg, args = reset_msg(msg, *args)
        if self.isEnabledFor(logging.WARNING):
            self._log(logging.WARNING, msg, args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'ERROR'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.error("Houston, we have a %s", "major problem", exc_info=1)
        """

        msg, args = reset_msg(msg, *args)
        if self.isEnabledFor(logging.ERROR):
            self._log(logging.ERROR, msg, args, **kwargs)

    def exception(self, msg, *args, exc_info=True, **kwargs):
        """
        Convenience method for logging an ERROR with exception information.
        """
        msg, args = reset_msg(msg, *args)
        self.error(msg, *args, exc_info=exc_info, **kwargs)

    def critical(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'CRITICAL'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.critical("Houston, we have a %s", "major disaster", exc_info=1)
        """
        msg, args = reset_msg(msg, *args)
        msg = "! " * 5 + msg
        if self.isEnabledFor(logging.CRITICAL):
            self._log(logging.CRITICAL, msg, args, **kwargs)


def logger_class_decorator():
    def wrapper(obj):
        obj.debug = LoggerTemplate.debug
        obj.info = LoggerTemplate.info
        obj.warning = LoggerTemplate.warning
        obj.error = LoggerTemplate.error
        obj.exception = LoggerTemplate.exception
        obj.critical = LoggerTemplate.critical
        return obj

    return wrapper


@logger_class_decorator()
class MyLogger(logging.Logger):
    pass


logger = get_my_logger("logging")

if __name__ == "__main__":
    # logger.debug('s')
    logger.debug(1, 213, 543)
    logger.info(1, 213, 543)
    logger.warning(1, 213, 543)
    logger.exception(1, 213, 543)
    logger.critical(1, 213, 543)
