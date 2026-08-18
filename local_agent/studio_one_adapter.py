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
        from adapters.manual_adapter import ManualAdapter
        return ManualAdapter(config)
    raise ValueError(f"未支持的 Studio One Adapter：{name}")
