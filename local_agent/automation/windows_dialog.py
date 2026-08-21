from __future__ import annotations

import ctypes
import time
from pathlib import Path


class FileDialogError(RuntimeError):
    pass


class WindowsFileDialog:
    EDIT_CLASS = "Edit"
    BUTTON_CLASS = "Button"
    WM_SETTEXT = 0x000C
    BM_CLICK = 0x00F5

    def __init__(self, timeout_seconds: int = 20, expected_process_id: int | None = None):
        self.timeout_seconds = timeout_seconds
        self.expected_process_id = expected_process_id

    @staticmethod
    def _children(parent: int) -> list[int]:
        user32 = ctypes.windll.user32
        children = []
        callback_type = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
        def callback(hwnd, _):
            children.append(int(hwnd)); return True
        user32.EnumChildWindows(parent, callback_type(callback), 0)
        return children

    @staticmethod
    def _text(hwnd: int) -> str:
        user32 = ctypes.windll.user32
        length = user32.GetWindowTextLengthW(hwnd)
        buffer = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buffer, length + 1)
        return buffer.value

    def _find_dialog(self) -> int | None:
        user32 = ctypes.windll.user32
        found = []
        callback_type = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
        def callback(hwnd, _):
            class_name = ctypes.create_unicode_buffer(256)
            user32.GetClassNameW(hwnd, class_name, 256)
            pid = ctypes.c_ulong()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            if class_name.value == "#32770" and user32.IsWindowVisible(hwnd) and (self.expected_process_id is None or int(pid.value) == self.expected_process_id):
                found.append(int(hwnd))
            return True
        user32.EnumWindows(callback_type(callback), 0)
        return found[0] if found else None

    def wait_for_file_dialog(self) -> int:
        deadline = time.monotonic() + self.timeout_seconds
        while time.monotonic() < deadline:
            dialog = self._find_dialog()
            if dialog:
                return dialog
            time.sleep(0.2)
        raise FileDialogError("Windows file dialog did not appear")

    def set_file_path(self, dialog: int, path: Path) -> None:
        if not path.is_file():
            raise FileDialogError(f"Input file does not exist: {path}")
        user32 = ctypes.windll.user32
        edits = []
        for child in self._children(dialog):
            class_name = ctypes.create_unicode_buffer(256)
            user32.GetClassNameW(child, class_name, 256)
            if class_name.value == self.EDIT_CLASS:
                edits.append(child)
        if not edits:
            raise FileDialogError("File dialog path edit control not found")
        user32.SendMessageW(edits[0], self.WM_SETTEXT, 0, str(path))

    def confirm_file_dialog(self, dialog: int) -> None:
        user32 = ctypes.windll.user32
        buttons = []
        for child in self._children(dialog):
            class_name = ctypes.create_unicode_buffer(256)
            user32.GetClassNameW(child, class_name, 256)
            if class_name.value == self.BUTTON_CLASS:
                label = self._text(child).lower().replace("&", "").replace("(", "").replace(")", "").strip()
                if "open" in label or "打开" in label or "确定" in label or "选择" in label:
                    buttons.append(child)
        if not buttons:
            # Some localized common dialogs expose no readable Button text.
            # Enter is the standard default action after the full path is set.
            user32.SetForegroundWindow(dialog)
            user32.PostMessageW(dialog, 0x0100, 0x0D, 0)
            user32.PostMessageW(dialog, 0x0101, 0x0D, 0)
            return
        user32.SendMessageW(buttons[0], self.BM_CLICK, 0, 0)

    def choose(self, path: Path, expected_process_id: int | None = None) -> None:
        if expected_process_id is not None:
            self.expected_process_id = expected_process_id
        dialog = self.wait_for_file_dialog()
        self.set_file_path(dialog, path)
        self.confirm_file_dialog(dialog)
