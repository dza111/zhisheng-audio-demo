from __future__ import annotations

import ctypes


class TrackSelectionError(RuntimeError):
    pass


def select_track_by_name(window_handle: int, track_name: str) -> None:
    """Select an exposed Studio One track control by its exact accessible name.

    Studio One's custom canvas may expose no UIA descendants. In that case we
    fail explicitly instead of guessing a row by position.
    """
    user32 = ctypes.windll.user32
    children: list[int] = []
    callback_type = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

    def callback(hwnd, _):
        children.append(int(hwnd))
        return True

    user32.EnumChildWindows(window_handle, callback_type(callback), 0)
    for child in children:
        length = user32.GetWindowTextLengthW(child)
        text = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(child, text, length + 1)
        if text.value == track_name:
            user32.SetFocus(child)
            return
    raise TrackSelectionError(f"找不到 Studio One 轨道控件: {track_name}")
