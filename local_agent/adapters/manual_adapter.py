from __future__ import annotations

import json
import os
import shutil
import time
from pathlib import Path

from studio_one_adapter import AdapterHealth, MixResult


class ManualAdapter:
    """Reliable phase-one handoff: Studio One exports a WAV into the job output folder."""

    def __init__(self, config: dict):
        self.config = config
        self.cancelled: set[str] = set()

    def healthcheck(self) -> AdapterHealth:
        template = str(self.config.get("studio_one_template", "")).strip()
        if str(self.config.get("manual_test_output", "")).lower() in {"1", "true", "yes"}:
            return AdapterHealth(True, "手动 Adapter 测试输出模式已就绪")
        if not template:
            return AdapterHealth(False, "未配置 Studio One 默认模板路径")
        if not Path(template).is_file():
            return AdapterHealth(False, f"找不到 Studio One 模板：{template}")
        return AdapterHealth(True, "手动 Studio One Adapter 已就绪")

    def process(self, job: dict, workspace: Path, progress_callback) -> MixResult:
        output_dir = workspace / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        manifest = {
            "job_id": job["job_id"],
            "template_id": job["plan"]["template_id"],
            "template_path": self.config.get("studio_one_template", ""),
            "track_mapping": job["track_mapping"],
            "inputs": job["inputs"],
            "instruction": "在 Studio One 打开默认模板，按轨道映射导入 inputs 文件夹，并将最终 WAV 导出到 output 文件夹。",
        }
        (workspace / "studio_one_job.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        progress_callback("preparing", "已准备本地工作目录和 Studio One 轨道映射")
        progress_callback("studio_processing", "测试执行模式：等待 Studio One 将最终 WAV 导出到本地 output 文件夹")

        # Explicit opt-in test mode makes the demo pipeline testable, but the result
        # remains labelled manual/test and is never presented as a Studio One render.
        if str(self.config.get("manual_test_output", "")).lower() in {"1", "true", "yes"}:
            source = next((Path(item["local_path"]) for item in job["inputs"] if item["format"] == "wav"), None)
            if source and source.is_file():
                target = output_dir / "TEST_MODE_SOURCE_COPY.wav"
                shutil.copy2(source, target)
                progress_callback("exporting", "测试执行模式：已生成测试输出文件")
                return MixResult(target, "manual_test")

        timeout = int(self.config.get("manual_timeout_seconds", 7200))
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if job["job_id"] in self.cancelled:
                raise RuntimeError("任务已取消")
            candidates = [path for path in output_dir.glob("*.wav") if path.stat().st_size > 44]
            if candidates:
                newest = max(candidates, key=lambda path: path.stat().st_mtime)
                progress_callback("exporting", "检测到 Studio One 导出的最终 WAV，正在上传")
                return MixResult(newest, "manual")
            time.sleep(2)
        raise TimeoutError("等待 Studio One 导出 WAV 超时")

    def cancel(self, job_id: str) -> bool:
        self.cancelled.add(job_id)
        return True
