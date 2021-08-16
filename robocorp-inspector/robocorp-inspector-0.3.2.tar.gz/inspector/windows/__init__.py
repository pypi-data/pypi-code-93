from .base import WindowState
from .browser import BrowserWindow
from .manager import ManagerWindow
from .image import ImageWindow

WINDOWS = {"browser": BrowserWindow, "image": ImageWindow, "manager": ManagerWindow}
