from ctypes import POINTER
from ctypes import WINFUNCTYPE
from ctypes import c_int
from ctypes import c_int64
from ctypes import c_void_p
from ctypes import windll
from ctypes.wintypes import ATOM
from ctypes.wintypes import BOOL
from ctypes.wintypes import DWORD
from ctypes.wintypes import HANDLE
from ctypes.wintypes import HBITMAP
from ctypes.wintypes import HDC
from ctypes.wintypes import HGDIOBJ
from ctypes.wintypes import HINSTANCE
from ctypes.wintypes import HMENU
from ctypes.wintypes import HMODULE
from ctypes.wintypes import HWND
from ctypes.wintypes import LPARAM
from ctypes.wintypes import LPCWSTR
from ctypes.wintypes import LPPOINT
from ctypes.wintypes import LPRECT
from ctypes.wintypes import RECT
from ctypes.wintypes import UINT
from ctypes.wintypes import WPARAM

INT_PTR = c_int64

DLGPROC = WINFUNCTYPE(INT_PTR, HWND, UINT, WPARAM, LPARAM)

# Window Styles
WS_OVERLAPPED = 0x00000000
WS_POPUP = 0x80000000
WS_CHILD = 0x40000000
WS_MINIMIZE = 0x20000000
WS_VISIBLE = 0x10000000
WS_DISABLED = 0x08000000
WS_CLIPSIBLINGS = 0x04000000
WS_CLIPCHILDREN = 0x02000000
WS_MAXIMIZE = 0x01000000
WS_CAPTION = 0x00C00000
WS_BORDER = 0x00800000
WS_DLGFRAME = 0x00400000
WS_VSCROLL = 0x00200000
WS_HSCROLL = 0x00100000
WS_SYSMENU = 0x00080000
WS_THICKFRAME = 0x00040000
WS_GROUP = 0x00020000
WS_TABSTOP = 0x00010000
WS_MINIMIZEBOX = 0x00020000
WS_MAXIMIZEBOX = 0x00010000
WS_TILED = WS_OVERLAPPED
WS_ICONIC = WS_MINIMIZE
WS_SIZEBOX = WS_THICKFRAME

# Extended Window Styles
WS_EX_DLGMODALFRAME = 0x00000001
WS_EX_NOPARENTNOTIFY = 0x00000004
WS_EX_TOPMOST = 0x00000008
WS_EX_ACCEPTFILES = 0x00000010
WS_EX_TRANSPARENT = 0x00000020
WS_EX_MDICHILD = 0x00000040
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_WINDOWEDGE = 0x00000100
WS_EX_CLIENTEDGE = 0x00000200
WS_EX_CONTEXTHELP = 0x00000400
WS_EX_RIGHT = 0x00001000
WS_EX_LEFT = 0x00000000
WS_EX_RTLREADING = 0x00002000
WS_EX_LTRREADING = 0x00000000
WS_EX_LEFTSCROLLBAR = 0x00004000
WS_EX_RIGHTSCROLLBAR = 0x00000000
WS_EX_CONTROLPARENT = 0x00010000
WS_EX_STATICEDGE = 0x00020000
WS_EX_APPWINDOW = 0x00040000
WS_EX_LAYERED = 0x00080000
WS_EX_NOINHERITLAYOUT = 0x00100000
WS_EX_NOREDIRECTIONBITMAP = 0x00200000
WS_EX_LAYOUTRTL = 0x00400000
WS_EX_COMPOSITED = 0x02000000
WS_EX_NOACTIVATE = 0x08000000
WS_EX_PALETTEWINDOW = WS_EX_WINDOWEDGE | WS_EX_TOOLWINDOW | WS_EX_TOPMOST

# Window Messages
WM_CLOSE = 0x0010
WM_CONTEXTMENU = 0x007B
WM_KEYDOWN = 0x0100
WM_INITDIALOG = 0x0110
WM_COMMAND = 0x0111

# Dialog Styles
DS_SETFONT = 0x0040
DS_MODALFRAME = 0x0080
DS_CENTER = 0x0800
DS_CENTERMOUSE = 0x1000

# Dialog Box Command IDs
IDOK = 1
IDCANCEL = 2
IDABORT = 3
IDRETRY = 4
IDIGNORE = 5
IDYES = 6
IDNO = 7
IDCLOSE = 8
IDHELP = 9
IDTRYAGAIN = 10
IDCONTINUE = 11

# Static Control Constants
SS_LEFT = 0x00000000
SS_CENTER = 0x00000001
SS_RIGHT = 0x00000002
SS_ICON = 0x00000003
SS_BLACKRECT = 0x00000004
SS_GRAYRECT = 0x00000005
SS_WHITERECT = 0x00000006
SS_BLACKFRAME = 0x00000007
SS_GRAYFRAME = 0x00000008
SS_WHITEFRAME = 0x00000009
SS_USERITEM = 0x0000000A
SS_SIMPLE = 0x0000000B
SS_LEFTNOWORDWRAP = 0x0000000C
SS_OWNERDRAW = 0x0000000D
SS_BITMAP = 0x0000000E
SS_ENHMETAFILE = 0x0000000F
SS_ETCHEDHORZ = 0x00000010
SS_ETCHEDVERT = 0x00000011
SS_ETCHEDFRAME = 0x00000012
SS_TYPEMASK = 0x0000001F
SS_REALSIZECONTROL = 0x00000040
SS_NOPREFIX = 0x00000080
SS_NOTIFY = 0x00000100
SS_CENTERIMAGE = 0x00000200
SS_RIGHTJUST = 0x00000400
SS_REALSIZEIMAGE = 0x00000800
SS_SUNKEN = 0x00001000
SS_EDITCONTROL = 0x00002000
SS_ENDELLIPSIS = 0x00004000
SS_PATHELLIPSIS = 0x00008000
SS_WORDELLIPSIS = 0x0000C000
SS_ELLIPSISMASK = 0x0000C000

# Edit Control Styles
ES_LEFT = 0x0000
ES_CENTER = 0x0001
ES_RIGHT = 0x0002
ES_MULTILINE = 0x0004
ES_UPPERCASE = 0x0008
ES_LOWERCASE = 0x0010
ES_PASSWORD = 0x0020
ES_AUTOVSCROLL = 0x0040
ES_AUTOHSCROLL = 0x0080
ES_NOHIDESEL = 0x0100
ES_OEMCONVERT = 0x0400
ES_READONLY = 0x0800
ES_WANTRETURN = 0x1000
ES_NUMBER = 0x2000

# Menu flags
MF_POPUP = 0x00000010
MF_HILITE = 0x00000080
MF_SEPARATOR = 0x00000800

# SetWindowPos Flags
SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0x0002
SWP_NOZORDER = 0x0004
SWP_NOREDRAW = 0x0008
SWP_NOACTIVATE = 0x0010
SWP_FRAMECHANGED = 0x0020
SWP_SHOWWINDOW = 0x0040
SWP_HIDEWINDOW = 0x0080
SWP_NOCOPYBITS = 0x0100
SWP_NOOWNERZORDER = 0x0200
SWP_NOSENDCHANGING = 0x0400
SWP_DEFERERASE = 0x2000
SWP_ASYNCWINDOWPOS = 0x4000

# DPI_AWARENESS_CONTEXT handle
DPI_AWARENESS_CONTEXT_UNAWARE = -1
DPI_AWARENESS_CONTEXT_SYSTEM_AWARE = -2
DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE = -3
DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2 = -4
DPI_AWARENESS_CONTEXT_UNAWARE_GDISCALED = -5

_AdjustWindowRectExForDpi = windll.user32.AdjustWindowRectExForDpi
_AdjustWindowRectExForDpi.argtypes = (LPRECT, DWORD, BOOL, DWORD, UINT)
_AdjustWindowRectExForDpi.restype = BOOL

_BitBlt = windll.gdi32.BitBlt
_BitBlt.argtypes = (HDC, c_int, c_int, c_int, c_int, HDC, c_int, c_int, DWORD)
_BitBlt.restype = BOOL

_ClientToScreen = windll.user32.ClientToScreen
_ClientToScreen.argtypes = (HWND, LPPOINT)
_ClientToScreen.restype = BOOL

_CreateCompatibleDC = windll.gdi32.CreateCompatibleDC
_CreateCompatibleDC.argtypes = (HDC,)
_CreateCompatibleDC.restype = HDC

_CreateDIBSection = windll.gdi32.CreateDIBSection
_CreateDIBSection.argtypes = (HDC, c_void_p, UINT, c_void_p, HANDLE, DWORD)
_CreateDIBSection.restype = HBITMAP

_DeleteDC = windll.gdi32.DeleteDC
_DeleteDC.argtypes = (HDC,)
_DeleteDC.restype = BOOL

_DeleteObject = windll.gdi32.DeleteObject
_DeleteObject.argtypes = (HGDIOBJ,)
_DeleteObject.restype = BOOL

_DestroyMenu = windll.user32.DestroyMenu
_DestroyMenu.argtypes = (HMENU,)
_DestroyMenu.restype = BOOL

_DialogBoxIndirectParamW = windll.user32.DialogBoxIndirectParamW
_DialogBoxIndirectParamW.argtypes = (HINSTANCE, c_void_p, HWND, c_void_p, LPARAM)
_DialogBoxIndirectParamW.restype = INT_PTR

_EndDialog = windll.user32.EndDialog
_EndDialog.argtypes = (HWND, INT_PTR)
_EndDialog.restype = BOOL

_FindWindowW = windll.user32.FindWindowW
_FindWindowW.argtypes = (LPCWSTR, LPCWSTR)
_FindWindowW.restype = HWND

_GetClassInfoExW = windll.user32.GetClassInfoExW
_GetClassInfoExW.argtypes = (HINSTANCE, LPCWSTR, c_void_p)
_GetClassInfoExW.restype = BOOL

_GetClientRect = windll.user32.GetClientRect
_GetClientRect.argtypes = (HWND, LPRECT)
_GetClientRect.restype = BOOL

_GetDC = windll.user32.GetDC
_GetDC.argtypes = (HWND,)
_GetDC.restype = HDC

_GetDesktopWindow = windll.user32.GetDesktopWindow
_GetDesktopWindow.restype = HWND

_GetDlgItem = windll.user32.GetDlgItem
_GetDlgItem.argtypes = (HWND, c_int)
_GetDlgItem.restype = HWND

_GetDlgItemInt = windll.user32.GetDlgItemInt
_GetDlgItemInt.argtypes = (HWND, c_int, POINTER(BOOL), BOOL)
_GetDlgItemInt.restype = UINT

_GetDpiForWindow = windll.user32.GetDpiForWindow
_GetDpiForWindow.argtypes = (HWND,)
_GetDpiForWindow.restype = UINT

_GetModuleHandleW = windll.kernel32.GetModuleHandleW
_GetModuleHandleW.argtypes = (LPCWSTR,)
_GetModuleHandleW.restype = HMODULE

_GetParent = windll.user32.GetParent
_GetParent.argtypes = (HWND,)
_GetParent.restype = HWND

_GetSubMenu = windll.user32.GetSubMenu
_GetSubMenu.argtypes = (HMENU, c_int)
_GetSubMenu.restype = HMENU

_GetWindowDC = windll.user32.GetWindowDC
_GetWindowDC.argtypes = (HWND,)
_GetWindowDC.restype = HDC

_GetWindowRect = windll.user32.GetWindowRect
_GetWindowRect.argtypes = (HWND, LPRECT)
_GetWindowRect.restype = BOOL

_LoadMenuIndirectW = windll.user32.LoadMenuIndirectW
_LoadMenuIndirectW.argtypes = (c_void_p,)
_LoadMenuIndirectW.restype = HMENU

_RegisterClassExW = windll.user32.RegisterClassExW
_RegisterClassExW.argtypes = (c_void_p,)
_RegisterClassExW.restype = ATOM

_ReleaseDC = windll.user32.ReleaseDC
_ReleaseDC.argtypes = (HWND, HDC)
_ReleaseDC.restype = c_int

_ScreenToClient = windll.user32.ScreenToClient
_ScreenToClient.argtypes = (HWND, LPPOINT)
_ScreenToClient.restype = BOOL

_SelectObject = windll.gdi32.SelectObject
_SelectObject.argtypes = (HDC, HGDIOBJ)
_SelectObject.restype = HGDIOBJ

_SetDlgItemInt = windll.user32.SetDlgItemInt
_SetDlgItemInt.argtypes = (HWND, c_int, UINT, BOOL)
_SetDlgItemInt.restype = BOOL

_SetFocus = windll.user32.SetFocus
_SetFocus.argtypes = (HWND,)
_SetFocus.restype = HWND

_SetThreadDpiAwarenessContext = windll.user32.SetThreadDpiAwarenessContext
_SetThreadDpiAwarenessContext.argtypes = (c_void_p,)
_SetThreadDpiAwarenessContext.restype = c_void_p

_SetWindowPos = windll.user32.SetWindowPos
_SetWindowPos.argtypes = (HWND, HWND, c_int, c_int, c_int, c_int, UINT)
_SetWindowPos.restype = BOOL

_SetWindowTextW = windll.user32.SetWindowTextW
_SetWindowTextW.argtypes = (HWND, LPCWSTR)
_SetWindowTextW.restype = BOOL

_TrackPopupMenuEx = windll.user32.TrackPopupMenuEx
_TrackPopupMenuEx.argtypes = (HMENU, UINT, c_int, c_int, HWND, POINTER(RECT))
_TrackPopupMenuEx.restype = BOOL
