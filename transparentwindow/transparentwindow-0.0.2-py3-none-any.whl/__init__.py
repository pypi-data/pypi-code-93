"""Transparent window

Example::

    >> from threading import Thread
    >> import transparentwindow as tw
    >> Thread(target=tw.show_tpwin).start()
    >> img = tw.capture_as_PIL_Image(*tw.get_tpwin_xywh())
    >> img.show()

"""
from transparentwindow._win import DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2
from transparentwindow._win import _SetThreadDpiAwarenessContext
from transparentwindow.transparentdlg import get_tpwin_hwnd
from transparentwindow.transparentdlg import get_tpwin_xywh
from transparentwindow.transparentdlg import show_tpwin

try:
    from transparentwindow.capture import capture_as_PIL_Image
except ImportError:
    pass
try:
    from transparentwindow.capture import capture_as_opencv_img
except ImportError:
    pass

_SetThreadDpiAwarenessContext(DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2)
