from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Protocol


ProgressCallback = Callable[[str, str], None]


@dataclass
class AdapterHealth:
    ready: bool
    message: str


@dataclass
class MixResult:
    output_path: Path
    execution_mode: str


class StudioOneAdapter(Protocol):
    """Stable boundary. Server and browser never import or control this adapter."""

    def healthcheck(self) -> AdapterHealth: ...

    def process(self, job: dict, workspace: Path, progress_callback: ProgressCallback) -> MixResult: ...

    def cancel(self, job_id: str) -> bool: ...


def get_adapter(name: str, config: dict) -> StudioOneAdapter:
    if name == "manual":
        try:
            from .adapters.manual_adapter import ManualAdapter
        except ImportError:
            from adapters.manual_adapter import ManualAdapter
        return ManualAdapter(config)
    if name in {"studio_one", "native_keys"}:
        try:
            from .adapters.studio_one_adapter import StudioOneAdapterImpl
        except ImportError:
            from adapters.studio_one_adapter import StudioOneAdapterImpl
        return StudioOneAdapterImpl(config)
    raise ValueError(f"未支持的 Studio One Adapter：{name}")
