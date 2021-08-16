from ctypes import Structure
from ctypes import byref
from ctypes import c_short
from ctypes.wintypes import BOOL
from ctypes.wintypes import DWORD
from ctypes.wintypes import HWND
from ctypes.wintypes import POINT
from ctypes.wintypes import RECT
from ctypes.wintypes import WCHAR
from ctypes.wintypes import WORD

from transparentwindow._win import DLGPROC
from transparentwindow._win import DS_CENTERMOUSE
from transparentwindow._win import DS_MODALFRAME
from transparentwindow._win import DS_SETFONT
from transparentwindow._win import ES_NUMBER
from transparentwindow._win import IDCANCEL
from transparentwindow._win import IDOK
from transparentwindow._win import SS_RIGHT
from transparentwindow._win import SWP_NOZORDER
from transparentwindow._win import WM_CLOSE
from transparentwindow._win import WM_COMMAND
from transparentwindow._win import WM_INITDIALOG
from transparentwindow._win import WS_BORDER
from transparentwindow._win import WS_CAPTION
from transparentwindow._win import WS_CHILD
from transparentwindow._win import WS_POPUP
from transparentwindow._win import WS_SYSMENU
from transparentwindow._win import WS_TABSTOP
from transparentwindow._win import WS_VISIBLE
from transparentwindow._win import _ClientToScreen
from transparentwindow._win import _DialogBoxIndirectParamW
from transparentwindow._win import _EndDialog
from transparentwindow._win import _GetClientRect
from transparentwindow._win import _GetDlgItem
from transparentwindow._win import _GetDlgItemInt
from transparentwindow._win import _GetWindowRect
from transparentwindow._win import _SetDlgItemInt
from transparentwindow._win import _SetFocus
from transparentwindow._win import _SetWindowPos
from transparentwindow._win import _SetWindowTextW

IDC_STATIC = -1
IDC_X = 201
IDC_Y = 202
IDC_W = 203
IDC_H = 204


class DialogTemplate(Structure):
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
        ("defaultclass", WORD),
        ("notitle", WCHAR),
        ("fontsize", WORD),
        ("fontfamily", WCHAR * 9),
        # Item
        ("xtext_itemstyle", DWORD),
        ("xtext_itemdwExtendedStyle", DWORD),
        ("xtext_itemx", c_short),
        ("xtext_itemy", c_short),
        ("xtext_itemcx", c_short),
        ("xtext_itemcy", c_short),
        ("xtext_itemid", WORD),
        ("xtext_itemcls", WORD * 2),
        ("xtext_itemtext", WCHAR * 3),
        ("xtext_itemdata", WORD * 2),
        # Item
        ("ytext_itemstyle", DWORD),
        ("ytext_itemdwExtendedStyle", DWORD),
        ("ytext_itemx", c_short),
        ("ytext_itemy", c_short),
        ("ytext_itemcx", c_short),
        ("ytext_itemcy", c_short),
        ("ytext_itemid", WORD),
        ("ytext_itemcls", WORD * 2),
        ("ytext_itemtext", WCHAR * 3),
        ("ytext_itemdata", WORD * 2),
        # Item
        ("wtext_itemstyle", DWORD),
        ("wtext_itemdwExtendedStyle", DWORD),
        ("wtext_itemx", c_short),
        ("wtext_itemy", c_short),
        ("wtext_itemcx", c_short),
        ("wtext_itemcy", c_short),
        ("wtext_itemid", WORD),
        ("wtext_itemcls", WORD * 2),
        ("wtext_itemtext", WCHAR * 7),
        ("wtext_itemdata", WORD * 2),
        # Item
        ("htext_itemstyle", DWORD),
        ("htext_itemdwExtendedStyle", DWORD),
        ("htext_itemx", c_short),
        ("htext_itemy", c_short),
        ("htext_itemcx", c_short),
        ("htext_itemcy", c_short),
        ("htext_itemid", WORD),
        ("htext_itemcls", WORD * 2),
        ("htext_itemtext", WCHAR * 8),
        ("htext_itemdata", WORD * 1),
        # Item
        ("xedit_itemstyle", DWORD),
        ("xedit_itemdwExtendedStyle", DWORD),
        ("xedit_itemx", c_short),
        ("xedit_itemy", c_short),
        ("xedit_itemcx", c_short),
        ("xedit_itemcy", c_short),
        ("xedit_itemid", WORD),
        ("xedit_itemcls", WORD * 2),
        ("xedit_itemtext", WCHAR * 2),
        ("xedit_itemdata", WORD * 1),
        # Item
        ("yedit_itemstyle", DWORD),
        ("yedit_itemdwExtendedStyle", DWORD),
        ("yedit_itemx", c_short),
        ("yedit_itemy", c_short),
        ("yedit_itemcx", c_short),
        ("yedit_itemcy", c_short),
        ("yedit_itemid", WORD),
        ("yedit_itemcls", WORD * 2),
        ("yedit_itemtext", WCHAR * 2),
        ("yedit_itemdata", WORD * 1),
        # Item
        ("wedit_itemstyle", DWORD),
        ("wedit_itemdwExtendedStyle", DWORD),
        ("wedit_itemx", c_short),
        ("wedit_itemy", c_short),
        ("wedit_itemcx", c_short),
        ("wedit_itemcy", c_short),
        ("wedit_itemid", WORD),
        ("wedit_itemcls", WORD * 2),
        ("wedit_itemtext", WCHAR * 2),
        ("wedit_itemdata", WORD * 1),
        # Item
        ("hedit_itemstyle", DWORD),
        ("hedit_itemdwExtendedStyle", DWORD),
        ("hedit_itemx", c_short),
        ("hedit_itemy", c_short),
        ("hedit_itemcx", c_short),
        ("hedit_itemcy", c_short),
        ("hedit_itemid", WORD),
        ("hedit_itemcls", WORD * 2),
        ("hedit_itemtext", WCHAR * 2),
        ("hedit_itemdata", WORD * 1),
    )

    def __init__(self) -> None:
        text_style = WS_CHILD | WS_VISIBLE | SS_RIGHT
        edit_style = WS_CHILD | WS_VISIBLE | WS_BORDER | WS_TABSTOP | ES_NUMBER
        super().__init__()
        self.style = (
            WS_POPUP
            | WS_CAPTION
            | WS_SYSMENU
            | DS_CENTERMOUSE
            | DS_MODALFRAME
            | DS_SETFONT
        )
        self.cdit = 8
        self.cx = 85
        self.cy = 80
        self.fontsize = 9
        self.fontfamily = "Segoe UI"
        self.xtext_itemstyle = text_style
        self.xtext_itemx = 10
        self.xtext_itemy = 11
        self.xtext_itemcx = 28
        self.xtext_itemcy = 10
        self.xtext_itemid = IDC_STATIC
        self.xtext_itemcls = (WORD * 2)(0xFFFF, 0x0082)
        self.xtext_itemtext = "X:"
        self.ytext_itemstyle = text_style
        self.ytext_itemx = 10
        self.ytext_itemy = 26
        self.ytext_itemcx = 28
        self.ytext_itemcy = 10
        self.ytext_itemid = IDC_STATIC
        self.ytext_itemcls = (WORD * 2)(0xFFFF, 0x0082)
        self.ytext_itemtext = "Y:"
        self.wtext_itemstyle = text_style
        self.wtext_itemx = 10
        self.wtext_itemy = 41
        self.wtext_itemcx = 28
        self.wtext_itemcy = 10
        self.wtext_itemid = IDC_STATIC
        self.wtext_itemcls = (WORD * 2)(0xFFFF, 0x0082)
        self.wtext_itemtext = "Width:"
        self.htext_itemstyle = text_style
        self.htext_itemx = 10
        self.htext_itemy = 56
        self.htext_itemcx = 28
        self.htext_itemcy = 10
        self.htext_itemid = IDC_STATIC
        self.htext_itemcls = (WORD * 2)(0xFFFF, 0x0082)
        self.htext_itemtext = "Height:"
        self.xedit_itemstyle = edit_style
        self.xedit_itemx = 41
        self.xedit_itemy = 10
        self.xedit_itemcx = 28
        self.xedit_itemcy = 10
        self.xedit_itemid = IDC_X
        self.xedit_itemcls = (WORD * 2)(0xFFFF, 0x0081)
        self.xedit_itemtext = "0"
        self.yedit_itemstyle = edit_style
        self.yedit_itemx = 41
        self.yedit_itemy = 25
        self.yedit_itemcx = 28
        self.yedit_itemcy = 10
        self.yedit_itemid = IDC_Y
        self.yedit_itemcls = (WORD * 2)(0xFFFF, 0x0081)
        self.yedit_itemtext = "0"
        self.wedit_itemstyle = edit_style
        self.wedit_itemx = 41
        self.wedit_itemy = 40
        self.wedit_itemcx = 28
        self.wedit_itemcy = 10
        self.wedit_itemid = IDC_W
        self.wedit_itemcls = (WORD * 2)(0xFFFF, 0x0081)
        self.wedit_itemtext = "0"
        self.hedit_itemstyle = edit_style
        self.hedit_itemx = 41
        self.hedit_itemy = 55
        self.hedit_itemcx = 28
        self.hedit_itemcy = 10
        self.hedit_itemid = IDC_H
        self.hedit_itemcls = (WORD * 2)(0xFFFF, 0x0081)
        self.hedit_itemtext = "0"


def show_posdlg(hwnd: HWND = None) -> None:
    w_rect = RECT()
    _GetWindowRect(hwnd, byref(w_rect))
    c_rect = RECT()
    _GetClientRect(hwnd, byref(c_rect))
    dw = (w_rect.right - w_rect.left) - (c_rect.right - c_rect.left)
    dh = (w_rect.bottom - w_rect.top) - (c_rect.bottom - c_rect.top)
    c_point = POINT()
    _ClientToScreen(hwnd, byref(c_point))
    dx = c_point.x - w_rect.left
    dy = c_point.y - w_rect.top

    @DLGPROC
    def DlgProc(hwnd_self: int, msg: int, wPalam: int, lPalam) -> int:
        if msg == WM_INITDIALOG:
            _SetWindowTextW(hwnd_self, "Position and Size")
            _SetDlgItemInt(hwnd_self, IDC_X, c_point.x, 1)
            _SetDlgItemInt(hwnd_self, IDC_Y, c_point.y, 1)
            _SetDlgItemInt(hwnd_self, IDC_W, c_rect.right, 1)
            _SetDlgItemInt(hwnd_self, IDC_H, c_rect.bottom, 1)
            _SetFocus(_GetDlgItem(hwnd_self, IDC_X))
        elif msg == WM_COMMAND:
            id = wPalam & 0xFFFF
            if id == IDOK:
                result = BOOL()
                x = _GetDlgItemInt(hwnd_self, IDC_X, byref(result), 1)
                if result.value == 0:
                    return 0
                y = _GetDlgItemInt(hwnd_self, IDC_Y, byref(result), 1)
                if result.value == 0:
                    return 0
                w = _GetDlgItemInt(hwnd_self, IDC_W, byref(result), 1)
                if result.value == 0:
                    return 0
                h = _GetDlgItemInt(hwnd_self, IDC_H, byref(result), 1)
                if result.value == 0:
                    return 0
                _SetWindowPos(hwnd, 0, x - dx, y - dy, w + dw, h + dh, SWP_NOZORDER)
            elif id == IDCANCEL:
                _EndDialog(hwnd_self, IDCANCEL)
                return 1
        elif msg == WM_CLOSE:
            _EndDialog(hwnd_self, IDOK)
            return 1
        return 0

    dlg = DialogTemplate()
    _DialogBoxIndirectParamW(None, byref(dlg), hwnd, DlgProc, 0)
