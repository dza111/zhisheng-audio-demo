from __future__ import annotations

import json
import os
import shutil
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .models import ACTIVE_STATUSES, ALLOWED_ROLES, DEFAULT_MIX_MODE, DEFAULT_TEMPLATE_ID, ROLE_TO_TRACK
from .uploads import safe_display_name


DATA_ROOT = Path(os.environ.get("MIX_DATA_DIR", "data")).resolve()
JOBS_DIR = DATA_ROOT / "jobs"
UPLOADS_DIR = DATA_ROOT / "uploads"
RESULTS_DIR = DATA_ROOT / "results"
STAGING_DIR = UPLOADS_DIR / "staging"
LOCK = threading.RLock()
JOBS: dict[str, dict] = {}
STAGING: dict[str, dict] = {}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_directories() -> None:
    for path in (JOBS_DIR, UPLOADS_DIR, RESULTS_DIR, STAGING_DIR):
        path.mkdir(parents=True, exist_ok=True)


def _write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def _job_path(job_id: str) -> Path:
    return JOBS_DIR / job_id / "job.json"


def persist(job: dict) -> None:
    folder = _job_path(job["job_id"]).parent
    folder.mkdir(parents=True, exist_ok=True)
    _write_json(folder / "job.json", job)


def restore() -> None:
    ensure_directories()
    with LOCK:
        for manifest in JOBS_DIR.glob("*/job.json"):
            try:
                job = json.loads(manifest.read_text(encoding="utf-8"))
                if isinstance(job.get("job_id"), str):
                    JOBS[job["job_id"]] = job
            except (OSError, json.JSONDecodeError):
                continue


def stage_upload(filename: str, extension: str, content: bytes, metadata: dict) -> dict:
    ensure_directories()
    file_id = f"file_{uuid.uuid4().hex}"
    path = STAGING_DIR / f"{file_id}.{extension}"
    path.write_bytes(content)
    record = {
        "file_id": file_id,
        "display_name": safe_display_name(filename),
        "extension": extension,
        "path": str(path),
        "size_bytes": len(content),
        **metadata,
    }
    with LOCK:
        STAGING[file_id] = record
    _write_json(STAGING_DIR / f"{file_id}.json", record)
    return record


def get_staged(file_id: str) -> dict | None:
    with LOCK:
        record = STAGING.get(file_id)
    if record:
        return record
    manifest = STAGING_DIR / f"{file_id}.json"
    if not manifest.exists():
        return None
    try:
        record = json.loads(manifest.read_text(encoding="utf-8"))
        with LOCK:
            STAGING[file_id] = record
        return record
    except (OSError, json.JSONDecodeError):
        return None


def create_job(upload_requests: list[dict], request: dict, plan: dict) -> dict:
    if not upload_requests or len(upload_requests) > int(os.environ.get("MIX_MAX_FILES", "4")):
        raise ValueError("请上传 1 到 4 个音频文件")
    job_id = f"mix_{uuid.uuid4().hex}"
    seen_roles: set[str] = set()
    inputs = []
    for item in upload_requests:
        role = str(item.get("role", ""))
        file_id = str(item.get("file_id", ""))
        if role not in ALLOWED_ROLES or role in seen_roles:
            raise ValueError("音频轨道类型无效或重复")
        staged = get_staged(file_id)
        if not staged or not Path(staged["path"]).is_file():
            raise ValueError("上传文件不存在或已过期")
        seen_roles.add(role)
        destination_dir = UPLOADS_DIR / job_id
        destination_dir.mkdir(parents=True, exist_ok=True)
        destination = destination_dir / f"{file_id}.{staged['extension']}"
        shutil.move(staged["path"], destination)
        (STAGING_DIR / f"{file_id}.json").unlink(missing_ok=True)
        with LOCK:
            STAGING.pop(file_id, None)
        inputs.append({
            "file_id": file_id,
            "role": role,
            "track_name": ROLE_TO_TRACK[role],
            "display_name": staged["display_name"],
            "format": staged["format"],
            "size_bytes": staged["size_bytes"],
            "sample_rate": staged.get("sample_rate"),
            "channels": staged.get("channels"),
            "duration_seconds": staged.get("duration_seconds"),
            "path": str(destination),
        })
    timestamp = now()
    job = {
        "job_id": job_id,
        "status": "queued",
        "created_at": timestamp,
        "updated_at": timestamp,
        "request": request,
        "plan": {
            "genre": plan.get("genre", "UNKNOWN"),
            "template_id": DEFAULT_TEMPLATE_ID,
            "mix_mode": DEFAULT_MIX_MODE,
            "reason": plan.get("reason", "已建立默认专业混音任务。"),
        },
        "inputs": inputs,
        "track_mapping": ROLE_TO_TRACK,
        "agent": {"agent_id": None, "claimed_at": None, "heartbeat_at": None},
        "progress": {"step": "queued", "message": "等待本地智能音频工作站领取任务"},
        "result": {"file_id": None, "display_name": None, "format": None, "path": None, "download_url": None, "duration_seconds": None, "execution_mode": os.environ.get("MIX_EXECUTION_MODE", "manual")},
        "error": None,
    }
    with LOCK:
        JOBS[job_id] = job
        persist(job)
    return job


def get_job(job_id: str) -> dict | None:
    with LOCK:
        return JOBS.get(job_id)


def update_job(job_id: str, status: str | None = None, message: str | None = None, **changes) -> dict:
    with LOCK:
        job = JOBS.get(job_id)
        if not job:
            raise KeyError("任务不存在")
        if status:
            if status not in ACTIVE_STATUSES | {"completed", "failed", "cancelled"}:
                raise ValueError("任务状态无效")
            job["status"] = status
            job["progress"]["step"] = status
        if message:
            job["progress"]["message"] = str(message)[:500]
        for key, value in changes.items():
            job[key] = value
        job["updated_at"] = now()
        persist(job)
        return job


def claim_next(agent_id: str) -> dict | None:
    with LOCK:
        for job in JOBS.values():
            if job["status"] != "queued":
                continue
            timestamp = now()
            job["status"] = "claimed"
            job["progress"] = {"step": "claimed", "message": "智能音频工作站已领取任务"}
            job["agent"] = {"agent_id": agent_id, "claimed_at": timestamp, "heartbeat_at": timestamp}
            job["updated_at"] = timestamp
            persist(job)
            return job
    return None


def heartbeat(job_id: str, agent_id: str) -> dict:
    with LOCK:
        job = JOBS.get(job_id)
        if not job:
            raise KeyError("任务不存在")
        if job.get("agent", {}).get("agent_id") != agent_id:
            raise PermissionError("任务不属于当前 Agent")
        job["agent"]["heartbeat_at"] = now()
        job["updated_at"] = now()
        persist(job)
        return job


def save_result(job_id: str, filename: str, content: bytes, metadata: dict) -> dict:
    if not content:
        raise ValueError("导出结果为空")
    with LOCK:
        job = JOBS.get(job_id)
        if not job:
            raise KeyError("任务不存在")
        result_id = f"result_{uuid.uuid4().hex}"
        folder = RESULTS_DIR / job_id
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / f"{result_id}.wav"
        path.write_bytes(content)
        job["result"] = {
            "file_id": result_id,
            "display_name": safe_display_name(filename) or "zhisheng_mix.wav",
            "format": "wav",
            "path": str(path),
            "download_url": f"/api/mixing/jobs/{job_id}/result",
            "duration_seconds": metadata.get("duration_seconds"),
            "sample_rate": metadata.get("sample_rate"),
            "execution_mode": os.environ.get("MIX_EXECUTION_MODE", "manual"),
        }
        job["status"] = "completed"
        job["progress"] = {"step": "completed", "message": "AI 混音完成，最终音频已上传"}
        job["updated_at"] = now()
        persist(job)
        return job


restore()
