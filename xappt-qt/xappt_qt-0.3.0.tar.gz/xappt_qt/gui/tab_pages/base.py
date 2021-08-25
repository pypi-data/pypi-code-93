from PyQt5 import QtWidgets

from typing import Callable


class BaseTabPage(QtWidgets.QWidget):
    def __init__(self, **kwargs):
        super().__init__()
        self._on_info: Callable = kwargs.get("on_info")
        self._on_warn: Callable = kwargs.get("on_warn")
        self._on_error: Callable = kwargs.get("on_error")

    def information(self, title: str, message: str):
        if self._on_info:
            self._on_info(title, message)
        else:
            print(f"{title}: {message}")

    def warning(self, title: str, message: str):
        if self._on_warn:
            self._on_warn(title, message)
        else:
            print(f"{title}: {message}")

    def critical(self, title: str, message: str):
        if self._on_error:
            self._on_error(title, message)
        else:
            print(f"{title}: {message}")
