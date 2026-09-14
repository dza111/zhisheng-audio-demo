"""Bring an off-screen Studio One Export Mixdown dialog back into view once.

This helper never closes, hides, minimizes, or changes the Studio One main
window.  It only moves the export dialog if its saved location lies outside
the visible desktop area, then exits.
"""

from __future__ import annotations

import ctypes
import time
from ctypes import wintypes


class RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long), ("right", ctypes.c_long), ("bottom", ctypes.c_long)]


USER32 = ctypes.WinDLL("user32", use_last_error=True)
SWP_NOZORDER = 0x0004
SWP_NOACTIVATE = 0x0010

USER32.SetWindowPos.argtypes = [
    wintypes.HWND,
    wintypes.HWND,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_uint,
]
USER32.SetWindowPos.restype = wintypes.BOOL


def find_export_dialog() -> int | None:
    found: list[int] = []
    callback_type = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)

    def callback(hwnd: int, _lparam: int) -> bool:
        class_name = ctypes.create_unicode_buffer(256)
        USER32.GetClassNameW(hwnd, class_name, len(class_name))
        title_length = USER32.GetWindowTextLengthW(hwnd)
        title = ctypes.create_unicode_buffer(title_length + 1)
        USER32.GetWindowTextW(hwnd, title, len(title))
        # Studio One can localize the dialog title differently.  The CCL
        # dialog class is sufficient here; the position check in restore()
        # ensures that only an off-screen dialog is moved.
        if USER32.IsWindowVisible(hwnd) and class_name.value == "CCLDialogClass":
            found.append(hwnd)
            return False
        return True

    USER32.EnumWindows(callback_type(callback), 0)
    return found[0] if found else None


def restore(hwnd: int) -> bool:
    rect = RECT()
    if not USER32.GetWindowRect(hwnd, ctypes.byref(rect)):
        return False
    width, height = rect.right - rect.left, rect.bottom - rect.top
    screen_width, screen_height = USER32.GetSystemMetrics(0), USER32.GetSystemMetrics(1)
    if rect.right > 0 and rect.left < screen_width and rect.bottom > 0 and rect.top < screen_height:
        return True
    target_x = max(40, (screen_width - width) // 2)
    target_y = max(40, (screen_height - height) // 2)
    return bool(USER32.SetWindowPos(hwnd, 0, target_x, target_y, width, height, SWP_NOZORDER | SWP_NOACTIVATE))


deadline = time.monotonic() + 180
while time.monotonic() < deadline:
    dialog = find_export_dialog()
    if dialog is not None and restore(dialog):
        break
    time.sleep(0.2)
