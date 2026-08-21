from __future__ import annotations

import ctypes
import os
import re
import subprocess
import time
from pathlib import Path

from .windows_dialog import FileDialogError, WindowsFileDialog


class StudioOneAutomationError(RuntimeError):
    pass


def select_formal_song(song_dir: Path, preferred_name: str = "") -> Path:
    candidates = sorted(
        path for path in song_dir.iterdir()
        if path.is_file() and path.suffix.lower() == ".song"
    )
    if not candidates:
        raise StudioOneAutomationError(f"No formal Studio One Song found in {song_dir}")
    if len(candidates) > 1:
        listing = "\n".join(f"{index}. {path}" for index, path in enumerate(candidates, 1))
        raise StudioOneAutomationError(f"MULTIPLE_STUDIO_ONE_SONG_FILES\n{listing}")
    if preferred_name and candidates[0].name != preferred_name:
        raise StudioOneAutomationError(f"Configured Studio One Song is not the unique formal Song: {candidates[0]}")
    return candidates[0]


class StudioOneAutomation:
    """Fixed Studio One demo automation using only verified Studio One macros."""

    def __init__(self, config: dict):
        self.config = config
        self.exe = Path(config.get("executable", r"C:\Program Files\Studio One 6\Studio One.exe"))
        self.title_hint = str(config.get("window_title_contains", "Studio One"))
        self.ready_timeout = int(config.get("ready_timeout_seconds", 120))
        self.export_timeout = int(config.get("export_timeout_seconds", 900))

    @staticmethod
    def _windows() -> list[tuple[int, str, int, str]]:
        user32 = ctypes.windll.user32
        result = []
        callback_type = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

        def callback(hwnd, _):
            length = user32.GetWindowTextLengthW(hwnd)
            if length:
                buffer = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buffer, length + 1)
                class_buffer = ctypes.create_unicode_buffer(256)
                user32.GetClassNameW(hwnd, class_buffer, 256)
                process_id = ctypes.c_ulong()
                user32.GetWindowThreadProcessId(hwnd, ctypes.byref(process_id))
                result.append((int(hwnd), buffer.value, int(process_id.value), class_buffer.value))
            return True

        user32.EnumWindows(callback_type(callback), 0)
        return result

    def _window(self) -> tuple[int, str, int, str] | None:
        hint = self.title_hint.lower()
        for item in self._windows():
            hwnd, title, process_id, class_name = item
            if hint not in title.lower() or not ctypes.windll.user32.IsWindowVisible(hwnd):
                continue
            if "gdi+ window" in title.lower() or "gdi+" in class_name.lower():
                continue
            kernel32 = ctypes.windll.kernel32
            access = 0x1000 | 0x0400
            process_handle = kernel32.OpenProcess(access, False, process_id)
            if not process_handle:
                continue
            try:
                buffer = ctypes.create_unicode_buffer(1024)
                size = ctypes.c_uint32(len(buffer))
                if not kernel32.QueryFullProcessImageNameW(process_handle, 0, buffer, ctypes.byref(size)):
                    continue
                if Path(buffer.value).name.lower() != self.exe.name.lower():
                    continue
            finally:
                kernel32.CloseHandle(process_handle)
            return item
        return None

    def _activate(self) -> None:
        window = self._window()
        if not window:
            raise StudioOneAutomationError("Studio One window not found")
        user32 = ctypes.windll.user32
        user32.SetForegroundWindow(window[0])
        time.sleep(0.15)

    def click_track(self, role: str) -> None:
        raise StudioOneAutomationError("Coordinate track selection is disabled; use select_first_track/select_next_track")

    @staticmethod
    def _send_keys(keys: str, step_delay: float = 0.02) -> None:
        if not keys:
            raise StudioOneAutomationError("Shortcut is not configured")
        token_map = {"ENTER": 0x0D, "ESC": 0x1B, "SPACE": 0x20, "TAB": 0x09, "HOME": 0x24, "F4": 0x73, "A": 0x41, "E": 0x45, "O": 0x4F, "V": 0x56, "Z": 0x5A, "F12": 0x7B}
        modifiers = {"^": 0x11, "+": 0x10, "%": 0x12}
        held = [modifiers[c] for c in keys if c in modifiers]
        match = re.search(r"\{([^}]+)\}|([A-Za-z])$", keys)
        if not match:
            raise StudioOneAutomationError(f"Unable to parse shortcut: {keys}")
        token = match.group(1) or match.group(2)
        vk = token_map.get(token.upper())
        if vk is None:
            raise StudioOneAutomationError(f"Unsupported shortcut: {keys}")
        ULONG_PTR = ctypes.c_ulonglong if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_ulong
        class KEYBDINPUT(ctypes.Structure):
            _fields_ = [("wVk", ctypes.c_ushort), ("wScan", ctypes.c_ushort), ("dwFlags", ctypes.c_uint32), ("time", ctypes.c_uint32), ("dwExtraInfo", ULONG_PTR)]
        class MOUSEINPUT(ctypes.Structure):
            _fields_ = [("dx", ctypes.c_long), ("dy", ctypes.c_long), ("mouseData", ctypes.c_uint32), ("dwFlags", ctypes.c_uint32), ("time", ctypes.c_uint32), ("dwExtraInfo", ULONG_PTR)]
        class INPUT_UNION(ctypes.Union):
            _fields_ = [("mi", MOUSEINPUT), ("ki", KEYBDINPUT)]
        class INPUT(ctypes.Structure):
            _anonymous_ = ("union",)
            _fields_ = [("type", ctypes.c_uint32), ("union", INPUT_UNION)]
        events = []
        for key in held:
            events.append((key, 0))
        events.append((vk, 0))
        events.append((vk, 2))
        for key in reversed(held):
            events.append((key, 2))
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        user32.SendInput.argtypes = [ctypes.c_uint, ctypes.POINTER(INPUT), ctypes.c_int]
        user32.SendInput.restype = ctypes.c_uint
        for key, flags in events:
            event = INPUT(type=1, ki=KEYBDINPUT(wVk=key, wScan=0, dwFlags=flags, time=0, dwExtraInfo=0))
            if user32.SendInput(1, ctypes.byref(event), ctypes.sizeof(INPUT)) != 1:
                error = ctypes.get_last_error()
                raise StudioOneAutomationError(f"SendInput failed for virtual key 0x{key:02X}, WinError={error}")
            time.sleep(step_delay)
        time.sleep(0.15)

    def healthcheck(self) -> tuple[bool, str]:
        if os.name != "nt":
            return False, "Studio One automation requires Windows"
        song_path = Path(str(self.config.get("song_path", "")))
        if not self.exe.is_file():
            return False, f"Studio One executable not found: {self.exe}"
        if song_path.suffix.lower() != ".song":
            return False, f"Configured path is not a formal .song: {song_path}"
        if not song_path.is_file():
            return False, f"Studio One song not found: {song_path}"
        return True, "Studio One executable and formal Song are ready"

    def launch_studio_one(self) -> None:
        if not self.exe.is_file():
            raise StudioOneAutomationError(f"Studio One executable not found: {self.exe}")
        if not self._window():
            subprocess.Popen([str(self.exe)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def open_song(self, song_path: Path) -> None:
        if not song_path.is_file():
            raise StudioOneAutomationError(f"Studio One song not found: {song_path}")
        window = self._window()
        if window and song_path.stem.lower() in window[1].lower():
            self._activate()
            return
        self.launch_studio_one()
        subprocess.Popen([str(self.exe), str(song_path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def wait_until_ready(self) -> None:
        deadline = time.monotonic() + self.ready_timeout
        while time.monotonic() < deadline:
            window = self._window()
            if window and "loading" not in window[1].lower() and "recovery" not in window[1].lower():
                self._activate()
                return
            time.sleep(1)
        raise StudioOneAutomationError("Studio One window not ready before timeout")

    def import_audio_to_track(self, audio_path: Path, role: str) -> None:
        if role not in {"accompaniment", "vocal"}:
            raise StudioOneAutomationError(f"Unsupported audio role: {role}")
        if role == "accompaniment":
            self.select_first_track()
        else:
            self.select_next_track()
        self.import_audio_to_selected_track(audio_path)

    def import_audio_to_selected_track(self, audio_path: Path) -> None:
        """Import into the track selected by a Studio One internal Macro."""
        try:
            self._activate()
            self._send_keys(self.config.get("import_macro_hotkey", "^+%{F12}"))
            window = self._window()
            if not window:
                raise StudioOneAutomationError("Studio One main window disappeared before file dialog")
            WindowsFileDialog(int(self.config.get("file_dialog_timeout_seconds", 20)), expected_process_id=window[2]).choose(audio_path)
            time.sleep(float(self.config.get("import_wait_seconds", 0.5)))
        except (FileDialogError, RuntimeError) as exc:
            raise StudioOneAutomationError(str(exc)) from exc

    def align_event_to_start(self) -> None:
        # The verified import Macro owns Studio One's default event placement.
        # Do not change markers, BPM, range, routing, or plugin settings.
        self._activate()

    @staticmethod
    def _send_ctrl_shift_alt_function_key(function_key_vk: int, step_delay: float = 0.04) -> None:
        """Send one Studio One Macro hotkey with native user32.SendInput only."""
        if function_key_vk not in range(0x70, 0x88):
            raise StudioOneAutomationError(f"Invalid function-key virtual key: {function_key_vk}")
        ULONG_PTR = ctypes.c_ulonglong if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_ulong

        class KEYBDINPUT(ctypes.Structure):
            _fields_ = [("wVk", ctypes.c_ushort), ("wScan", ctypes.c_ushort), ("dwFlags", ctypes.c_uint32), ("time", ctypes.c_uint32), ("dwExtraInfo", ULONG_PTR)]

        class MOUSEINPUT(ctypes.Structure):
            _fields_ = [("dx", ctypes.c_long), ("dy", ctypes.c_long), ("mouseData", ctypes.c_uint32), ("dwFlags", ctypes.c_uint32), ("time", ctypes.c_uint32), ("dwExtraInfo", ULONG_PTR)]

        class INPUT_UNION(ctypes.Union):
            _fields_ = [("mi", MOUSEINPUT), ("ki", KEYBDINPUT)]

        class INPUT(ctypes.Structure):
            _anonymous_ = ("union",)
            _fields_ = [("type", ctypes.c_uint32), ("union", INPUT_UNION)]

        # Ctrl down, Shift down, Alt down, Fn down/up, Alt up, Shift up, Ctrl up.
        events = [(0x11, 0), (0x10, 0), (0x12, 0), (function_key_vk, 0), (function_key_vk, 2), (0x12, 2), (0x10, 2), (0x11, 2)]
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        user32.SendInput.argtypes = [ctypes.c_uint, ctypes.POINTER(INPUT), ctypes.c_int]
        user32.SendInput.restype = ctypes.c_uint
        for virtual_key, flags in events:
            event = INPUT(type=1, ki=KEYBDINPUT(wVk=virtual_key, wScan=0, dwFlags=flags, time=0, dwExtraInfo=0))
            if user32.SendInput(1, ctypes.byref(event), ctypes.sizeof(INPUT)) != 1:
                raise StudioOneAutomationError(f"SendInput failed for virtual key 0x{virtual_key:02X}, WinError={ctypes.get_last_error()}")
            time.sleep(step_delay)
        time.sleep(0.2)

    def select_first_track(self) -> None:
        self._activate()
        self._send_ctrl_shift_alt_function_key(int(self.config.get("first_track_macro_vk", 0x79)))

    def select_next_track(self) -> None:
        self._activate()
        self._send_ctrl_shift_alt_function_key(int(self.config.get("next_track_macro_vk", 0x7A)))

    def run_next_track_probe(self) -> None:
        self._activate()
        self._send_ctrl_shift_alt_function_key(int(self.config.get("next_track_probe_macro_vk", 0x78)))

    def export_mixdown(self, output_format: str = "mp3") -> None:
        if output_format.lower() != "mp3":
            raise StudioOneAutomationError("Only MP3 export is supported")
        self._activate()
        self._send_keys(self.config.get("export_shortcut", "^e"))
        deadline = time.monotonic() + float(self.config.get("export_dialog_timeout_seconds", 15))
        while time.monotonic() < deadline:
            if any(item[3] == "CCLDialogClass" and "导出混音" in item[1] for item in self._windows()):
                self._send_vk(0x0D)
                return
            time.sleep(0.25)
        raise StudioOneAutomationError("Export Mixdown dialog was not detected")

    @staticmethod
    def _send_vk(virtual_key: int, step_delay: float = 0.04) -> None:
        ULONG_PTR = ctypes.c_ulonglong if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_ulong
        class KEYBDINPUT(ctypes.Structure):
            _fields_ = [("wVk", ctypes.c_ushort), ("wScan", ctypes.c_ushort), ("dwFlags", ctypes.c_uint32), ("time", ctypes.c_uint32), ("dwExtraInfo", ULONG_PTR)]
        class MOUSEINPUT(ctypes.Structure):
            _fields_ = [("dx", ctypes.c_long), ("dy", ctypes.c_long), ("mouseData", ctypes.c_uint32), ("dwFlags", ctypes.c_uint32), ("time", ctypes.c_uint32), ("dwExtraInfo", ULONG_PTR)]
        class INPUT_UNION(ctypes.Union):
            _fields_ = [("mi", MOUSEINPUT), ("ki", KEYBDINPUT)]
        class INPUT(ctypes.Structure):
            _anonymous_ = ("union",)
            _fields_ = [("type", ctypes.c_uint32), ("union", INPUT_UNION)]
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        user32.SendInput.argtypes = [ctypes.c_uint, ctypes.POINTER(INPUT), ctypes.c_int]
        user32.SendInput.restype = ctypes.c_uint
        for flags in (0, 2):
            event = INPUT(type=1, ki=KEYBDINPUT(wVk=virtual_key, wScan=0, dwFlags=flags, time=0, dwExtraInfo=0))
            if user32.SendInput(1, ctypes.byref(event), ctypes.sizeof(INPUT)) != 1:
                raise StudioOneAutomationError(f"SendInput failed for virtual key 0x{virtual_key:02X}")
            time.sleep(step_delay)

    @staticmethod
    def snapshot_mixdown(mixdown_dir: Path) -> dict[str, dict[str, int]]:
        return {
            item.name: {"mtime_ns": item.stat().st_mtime_ns, "size": item.stat().st_size}
            for item in mixdown_dir.glob("*.mp3") if item.is_file()
        }

    def wait_for_export(self, result_path: Path, before: dict | None = None) -> Path:
        before = before or {}
        mixdown_dir = result_path.parent
        deadline = time.monotonic() + self.export_timeout
        while time.monotonic() < deadline:
            for item in mixdown_dir.glob("*.mp3"):
                if not item.is_file():
                    continue
                stat = item.stat()
                previous = before.get(item.name, {})
                changed = stat.st_mtime_ns != previous.get("mtime_ns") or stat.st_size != previous.get("size")
                if changed and stat.st_size > 0:
                    size = stat.st_size
                    time.sleep(1)
                    if item.exists() and item.stat().st_size == size:
                        try:
                            with item.open("rb") as stream:
                                if stream.read(16):
                                    return item
                        except OSError:
                            pass
            time.sleep(2)
        raise StudioOneAutomationError(f"New stable MP3 was not generated: {result_path}")

    def close_song(self) -> None:
        self._activate()
        self._send_keys("^w")

    def close_studio_one(self) -> None:
        self._activate()
        self._send_keys("%{F4}")
