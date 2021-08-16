from ctypes import POINTER
from ctypes import Structure
from ctypes import byref
from ctypes import c_ubyte
from ctypes import sizeof
from ctypes.wintypes import DWORD
from ctypes.wintypes import LONG
from ctypes.wintypes import WORD

from transparentwindow._win import _BitBlt
from transparentwindow._win import _CreateCompatibleDC
from transparentwindow._win import _CreateDIBSection
from transparentwindow._win import _DeleteDC
from transparentwindow._win import _DeleteObject
from transparentwindow._win import _GetDesktopWindow
from transparentwindow._win import _GetWindowDC
from transparentwindow._win import _ReleaseDC
from transparentwindow._win import _SelectObject

SRCCOPY = 0x00CC0020


class BITMAPINFOHEADER(Structure):
    _pack_ = 1
    _fields_ = (
        ("biSize", DWORD),
        ("biWidth", LONG),
        ("biHeight", LONG),
        ("biPlanes", WORD),
        ("biBitCount", WORD),
        ("biCompression", DWORD),
        ("biSizeImage", DWORD),
        ("biXPelsPerMeter", LONG),
        ("biYPelsPerMeter", LONG),
        ("biClrUsed", DWORD),
        ("biClrImportant", DWORD),
    )


class BITMAPINFO(Structure):
    _pack_ = 1
    _fields_ = (
        ("bmiHeader", BITMAPINFOHEADER),
        ("bmiColors_nothing", LONG),
    )


class BITMAPFILEHEADER(Structure):
    _pack_ = 1
    _fields_ = (
        ("bfType", WORD),
        ("bfSize", DWORD),
        ("bfReserved1", WORD),
        ("bfReserved2", WORD),
        ("bfOffBits", DWORD),
    )

    def __init__(self, dwBmpSize: int) -> None:
        super().__init__()
        self.bfType = 0x4D42  # BM
        self.bfOffBits = sizeof(BITMAPFILEHEADER) + sizeof(BITMAPINFOHEADER)
        self.bfSize = self.bfOffBits + dwBmpSize


def _calc_bmp_size(width: int, height: int, bit_per_pixel: int) -> int:
    return int((width * bit_per_pixel + 31) / 32) * 4 * height


def _screen_capture(
    x: int, y: int, width: int, height: int, bit_per_pixel: int = 24
) -> bytes:
    """
    Returns:
        A byte buffer containing raw data.
    """
    bmi = BITMAPINFO()
    bmi.bmiHeader.biSize = sizeof(BITMAPINFOHEADER)
    bmi.bmiHeader.biWidth = width
    bmi.bmiHeader.biHeight = height
    bmi.bmiHeader.biPlanes = 1
    bmi.bmiHeader.biBitCount = bit_per_pixel
    # bmi.bmiHeader.biCompression = 0  # BI_RGB

    bmp_size = _calc_bmp_size(width, height, bit_per_pixel)

    hwnd = _GetDesktopWindow()
    p_pixels = POINTER(c_ubyte * bmp_size)()
    hdc_src = _GetWindowDC(hwnd)
    hdc_dst = _CreateCompatibleDC(hdc_src)
    hbmp_dst = _CreateDIBSection(None, byref(bmi), 0, byref(p_pixels), None, 0)
    _SelectObject(hdc_dst, hbmp_dst)

    _BitBlt(hdc_dst, 0, 0, width, height, hdc_src, x, y, SRCCOPY)

    _ReleaseDC(hwnd, hdc_src)
    ret = bytes(p_pixels.contents)
    _DeleteObject(hbmp_dst)
    _DeleteDC(hdc_dst)
    return ret


try:
    from PIL import Image
except ImportError:
    pass
else:

    def capture_as_PIL_Image(x: int, y: int, width: int, height: int) -> Image.Image:
        """
        Returns:
            a PIL image.

        Example::

            >> import transparentwindow as tw
            >> img = tw.capture_as_PIL_Image(0, 0, 100, 100)
            >> img.save("capture.png")

        """
        raw = _screen_capture(x, y, width, height, 24)
        img = Image.frombytes("RGB", (width, height), raw, "raw", "BGR", 0, -1)
        return img


try:
    from cv2 import COLOR_BGRA2BGR
    from cv2 import cvtColor
    from cv2 import flip
    from numpy import frombuffer
    from numpy import ndarray
    from numpy import uint8
except ImportError:
    pass
else:

    def capture_as_opencv_img(x: int, y: int, width: int, height: int) -> ndarray:
        """
        Returns:
            an image in NumPy.

        Example::

            >> import transparentwindow as tw
            >> import cv2 as cv
            >> img = tw.capture_as_opencv_img(0, 0, 100, 100)
            >> cv.imwrite("capture.png", img)

        """
        raw = _screen_capture(x, y, width, height, 32)
        img = frombuffer(raw, dtype=uint8).reshape((height, width, 4))
        return flip(cvtColor(img, COLOR_BGRA2BGR), 0)
