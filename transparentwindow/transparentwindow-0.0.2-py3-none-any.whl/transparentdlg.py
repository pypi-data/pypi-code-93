from ctypes import Structure
from ctypes import byref
from ctypes import c_int
from ctypes import c_short
from ctypes import c_void_p
from ctypes import sizeof
from ctypes.wintypes import DWORD
from ctypes.wintypes import HBRUSH
from ctypes.wintypes import HICON
from ctypes.wintypes import HINSTANCE
from ctypes.wintypes import HWND
from ctypes.wintypes import LPCWSTR
from ctypes.wintypes import POINT
from ctypes.wintypes import RECT
from ctypes.wintypes import UINT
from ctypes.wintypes import WCHAR
from ctypes.wintypes import WORD
from typing import Any
from typing import Callable

from transparentwindow._win import DLGPROC
from transparentwindow._win import DS_CENTER
from transparentwindow._win import DS_MODALFRAME
from transparentwindow._win import DS_SETFONT
from transparentwindow._win import IDCANCEL
from transparentwindow._win import MF_HILITE
from transparentwindow._win import MF_POPUP
from transparentwindow._win import MF_SEPARATOR
from transparentwindow._win import WM_CLOSE
from transparentwindow._win import WM_COMMAND
from transparentwindow._win import WM_CONTEXTMENU
from transparentwindow._win import WM_INITDIALOG
from transparentwindow._win import WM_KEYDOWN
from transparentwindow._win import WS_CAPTION
from transparentwindow._win import WS_EX_NOREDIRECTIONBITMAP
from transparentwindow._win import WS_EX_TOPMOST
from transparentwindow._win import WS_POPUP
from transparentwindow._win import WS_SIZEBOX
from transparentwindow._win import WS_SYSMENU
from transparentwindow._win import _ClientToScreen
from transparentwindow._win import _DestroyMenu
from transparentwindow._win import _DialogBoxIndirectParamW
from transparentwindow._win import _EndDialog
from transparentwindow._win import _FindWindowW
from transparentwindow._win import _GetClassInfoExW
from transparentwindow._win import _GetClientRect
from transparentwindow._win import _GetModuleHandleW
from transparentwindow._win import _GetSubMenu
from transparentwindow._win import _LoadMenuIndirectW
from transparentwindow._win import _RegisterClassExW
from transparentwindow._win import _SetWindowTextW
from transparentwindow._win import _TrackPopupMenuEx
from transparentwindow.posdlg import show_posdlg

CLASS_NAME = "Transparent_Window@Python"
CLASS_NAME_LEN = len(CLASS_NAME) + 1
IDM_POS = 101

_hinst = _GetModuleHandleW(None)


class _TransparentWindowClass(Structure):
    _pack_ = 1
    _fields_ = (
        ("cbSize", UINT),
        ("style", UINT),
        ("lpfnWndProc", c_void_p),
        ("cbClsExtra", c_int),
        ("cbWndExtra", c_int),
        ("hInstance", HINSTANCE),
        ("hIcon", HICON),
        ("hCursor", c_void_p),
        ("hbrBackground", HBRUSH),
        ("lpszMenuName", LPCWSTR),
        ("lpszClassName", LPCWSTR),
        ("hIconSm", HICON),
    )

    def __init__(self) -> None:
        super().__init__()
        if _GetClassInfoExW(_hinst, "#32770", byref(self)) == 0:
            raise OSError("Failed to retrieve information about a dialog window class.")
        self.cbSize = sizeof(self)
        self.hInstance = _hinst
        self.cbWndExtra = 30  # DLGWINDOWEXTRA
        self.lpszClassName = CLASS_NAME


class _MenuTemplate(Structure):
    _pack_ = 2
    _fields_ = (
        # header
        ("versionNumber", WORD),
        ("offset", WORD),
        # menu popup
        ("mtOption", WORD),
        ("mtString", WCHAR * 5),
        # menu item, Position dialog
        ("pos_mtOption", WORD),
        ("pos_mtID", WORD),
        ("pos_mtString", WCHAR * 18),
        # menu item, Separator
        ("sep_mtOption", WORD),
        ("sep_mtID", WORD),
        ("sep_mtString", WCHAR),
        # menu item, Close
        ("close_mtOption", WORD),
        ("close_mtID", WORD),
        ("close_mtString", WCHAR * 6),
    )

    def __init__(self) -> None:
        super().__init__()
        self.mtOption = MF_POPUP | MF_HILITE
        self.mtString = "Menu"
        self.pos_mtID = IDM_POS
        self.pos_mtString = "Position and Size"
        self.sep_mtOption = MF_SEPARATOR
        self.close_mtOption = MF_HILITE
        self.close_mtID = IDCANCEL
        self.close_mtString = "Close"


class _DialogTemplate(Structure):
    _pack_ = 2
    _fields_ = (
        ("style", DWORD),
        ("dwExtendedStyle", DWORD),
        ("cdit", WORD),
        ("x", c_short),
        ("y", c_short),
        ("cx", c_short),
        ("cy", c_short),
        ("nomenu", WORD),
        ("wndclass", WCHAR * CLASS_NAME_LEN),
        ("notitle", WCHAR),
        ("fontsize", WORD),
        ("fontfamily", WCHAR * 9),
    )

    def __init__(self) -> None:
        super().__init__()
        self.style = (
            WS_POPUP
            | WS_CAPTION
            | WS_SYSMENU
            | WS_SIZEBOX
            | DS_CENTER
            | DS_MODALFRAME
            | DS_SETFONT
        )
        self.dwExtendedStyle = WS_EX_NOREDIRECTIONBITMAP | WS_EX_TOPMOST
        self.cx = 160
        self.cy = 90
        self.wndclass = CLASS_NAME
        self.fontsize = 9
        self.fontfamily = "Segoe UI"


def show_tpwin(
    hwnd: HWND = None, title: str = "Python", callback: Callable[[int], Any] = None
) -> None:
    """Show a transparent window.

    Args:
        hwnd: a handle to the window that owns the transparent window.
        title: a title of the transparent window.
        callback: a callable type that is called when a key is pressed.

    Note:
        Window Class Name: "Transparent_Window@Python"

    Example::

        >> import transparentwindow as tw
        >> tw.show_tpwin(callback=lambda k: print(k, chr(k)))

    """

    @DLGPROC
    def _DlgProc(hwnd: int, msg: int, wPalam: int, lPalam) -> int:
        if msg == WM_INITDIALOG:
            _SetWindowTextW(hwnd, title)
        elif msg == WM_CONTEXTMENU:
            menu_tmpl = _MenuTemplate()
            hmenu = _LoadMenuIndirectW(byref(menu_tmpl))
            popup_menu = _GetSubMenu(hmenu, 0)
            x = lPalam & 0xFFFF
            y = (lPalam >> 16) & 0xFFFF
            _TrackPopupMenuEx(popup_menu, 0, x, y, hwnd, None)
            _DestroyMenu(hmenu)
            return 1
        elif msg == WM_COMMAND:
            id = wPalam & 0xFFFF
            if id == IDM_POS:
                show_posdlg(hwnd)
            elif id == IDCANCEL:
                _EndDialog(hwnd, IDCANCEL)
                return 1
        elif msg == WM_KEYDOWN:
            if callable(callback):
                callback(wPalam)
        elif msg == WM_CLOSE:
            _EndDialog(hwnd, 0)
            return 1
        return 0

    _DialogBoxIndirectParamW(None, byref(_DialogTemplate()), hwnd, _DlgProc, 0)


def get_tpwin_hwnd(title: str = None) -> int:
    """return the hwnd of a transparent window."""
    ret = _FindWindowW("Transparent_Window@Python", title)
    if ret:
        return ret
    else:
        raise OSError("Failed to find a transparent window.")


def get_tpwin_xywh(title: str = None) -> tuple[int, int, int, int]:
    """return the position and size of a transparent window.

    Args:
        title: the title of a transparent window.

    Returns:
        (x, y, width, height)

    Example::

        >> from threading import Thread
        >> import transparentwindow as tw
        >> Thread(target=tw.show_tpwin).start()
        >> img = tw.capture_as_PIL_Image(*tw.get_tpwin_xywh())
        >> img.show()

    """
    hwnd = get_tpwin_hwnd(title)
    point = POINT()
    _ClientToScreen(hwnd, byref(point))
    rect = RECT()
    _GetClientRect(hwnd, byref(rect))
    return point.x, point.y, rect.right, rect.bottom


_wc = _TransparentWindowClass()
if _RegisterClassExW(byref(_wc)) == 0:
    raise OSError("Failed to register a window class.")
