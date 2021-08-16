import logging
import platform
import threading
from pathlib import Path

_lock = threading.Lock()


class Log(object):
    """
        为简化日志的使用，通过实例化此类，并给定一个名称即可得到一个默认配置的logger，默认配置的logger同时向终端和日志文件写日志，
        终端和日志文件的日志级别均为info级别，执行的系统如果是windows，则日志文件默认保存在此包中的logs文件夹下，如果是Linux系统，则日志
        文件保存到/var/log/日志名称/ 目录下，日志文件名为：日志名.log，同时此日志还可以参照初始化参数说明进行日志配置的定制，此类为实例化
        为单例模式
    @author:redrose2100
    @version:1.0.1 发布
    @create_time：2021/08/16
    """
    _instance = None
    _is_init = False

    def __new__(cls, *args, **kwargs):
        """
        控制类的实例化，线程安全的单例模式
        :param args:
        :param kwargs:
        """
        with _lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, name="caterpillar_common", console_level=logging.INFO, file_level=logging.INFO,
                 log_fmt="%(asctime)s | %(levelname)s | %(pathname)s:%(lineno)s | %(message)s"):
        """
        Log 类初始化函数
        :param name: logger的名称，默认值为：caterpillar_common
        :param console_level: 终端日志级别，默认值为logging.INFO
        :param file_level: 日志文件中的日志级别，默认为loging.INFO
        :param log_fmt: 日志打印的格式，默认为 %(asctime)s | %(levelname)s | %(pathname)s:%(lineno)s | %(message)s
        """
        if self.__class__._is_init:
            return
        self.__name = name
        self.__console_level = console_level
        self.__file_level = file_level
        self.__log_fmt = log_fmt
        if platform.system() == "Linux":
            self.__log_file = f"/var/log/{self.__name}/{self.__name}.log"
            self.__log_dir = f"/var/log/{self.__name}"
        else:
            self.__log_file = Path(__file__).resolve().parent.parent / f"logs/{self.__name}.log"
            self.__log_dir = Path(__file__).resolve().parent.parent / "logs"

        if not Path(self.__log_dir).exists():
            Path.mkdir(parents=True, exist_ok=True)

        self.__logger = logging.getLogger(self.__name)
        self.__logger.setLevel(logging.DEBUG)
        self.__console_handler = logging.StreamHandler()
        self.__console_handler.setLevel(self.__console_level)
        self.__file_handler = logging.FileHandler(filename=self.__log_file)
        self.__file_handler.setLevel(self.__file_level)
        self.__formatter = logging.Formatter(fmt=self.__log_fmt)
        self.__console_handler.setFormatter(self.__formatter)
        self.__file_handler.setFormatter(self.__formatter)
        self.__logger.addHandler(self.__console_handler)
        self.__logger.addHandler(self.__file_handler)
        self.__class__._is_init = True

logger=Log()