from __future__ import annotations

from .studio_one_automation import StudioOneAutomation, StudioOneAutomationError


class TrackNavigationError(RuntimeError):
    pass


class TrackNavigator:
    """Fixed two-track navigation; never inspects Studio One track names."""

    def __init__(self, automation: StudioOneAutomation):
        self.automation = automation

    def _run_verified(self, key: str, label: str) -> None:
        if not key:
            raise TrackNavigationError(f"未验证 {label} 的 Studio One 轨道导航快捷键")
        try:
            self.automation._activate()
            self.automation._send_keys(key)
        except StudioOneAutomationError as exc:
            raise TrackNavigationError(str(exc)) from exc

    def select_first_track(self) -> None:
        self._run_verified(str(self.automation.config.get("first_track_hotkey", "")), "第 1 条轨道")

    def select_second_track(self) -> None:
        self._run_verified(str(self.automation.config.get("second_track_hotkey", "")), "第 2 条轨道")
