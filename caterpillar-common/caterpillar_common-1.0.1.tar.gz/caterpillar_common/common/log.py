import logging
import platform
import threading
from pathlib import Path

_lock=threading.Lock()


class Log(object):
    _instance=None
    _is_init=False
    def __new__(cls, *args, **kwargs):
        with _lock:
            if not cls._instance:
                cls._instance=super().__new__(*args,**kwargs)
        return cls._instance

    def __init__(self, name="caterpillar_common", console_level=logging.INFO, file_level=logging.INFO,
                 log_fmt="%(asctime)s | %(levelname)s | %(pathname)s:%(lineno)s | %(message)s"):
        if self.__class__._is_init:
            return
        self.__name = name
        self.__console_level = console_level
        self.__file_level = file_level
        self.__log_fmt=log_fmt
        if platform.system() == "Linux":
            self.__log_file = f"/var/log/{self.__name}/{self.__name}.log"
            self.__log_dir=f"/var/log/{self.__name}"
        else:
            self.__log_file = Path(__file__).resolve().parent.parent / f"logs/{self.__name}.log"
            self.__log_dir=Path(__file__).resolve().parent.parent / "logs"

        if not Path(self.__log_dir).exists():
            Path.mkdir(parents=True,exist_ok=True)

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
        self.__class__._is_init=True
