from __future__ import annotations

import json
import os
from pathlib import Path
from urllib.parse import quote

from . import planner, store
from .models import ALLOWED_ROLES, public_job
from .uploads import UploadError, inspect_audio, parse_multipart


def _read_body(handler, maximum: int) -> bytes:
    try:
        length = int(handler.headers.get("Content-Length", "0"))
    except ValueError as exc:
        raise UploadError("请求长度无效") from exc
    if length <= 0 or length > maximum:
        raise UploadError("文件过大或请求为空")
    return handler.rfile.read(length)


def _json_body(handler, maximum: int = 1024 * 1024) -> dict:
    raw = _read_body(handler, maximum)
    try:
        value = json.loads(raw.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise UploadError("请求 JSON 格式错误") from exc
    if not isinstance(value, dict):
        raise UploadError("请求 JSON 格式错误")
    return value


def _agent_allowed(handler) -> bool:
    # For the local demo, share the Agent's ignored .env as the single source
    # of truth. CloudBase does not have this local file, so it continues to use
    # MIX_AGENT_TOKEN from its configured environment.
    expected = os.environ.get("MIX_AGENT_TOKEN", "").strip()
    local_env = Path(__file__).resolve().parent.parent / "local_agent" / ".env"
    if local_env.is_file():
        try:
            for raw_line in local_env.read_text(encoding="utf-8-sig").splitlines():
                line = raw_line.strip()
                if line.startswith("MIX_AGENT_TOKEN="):
                    expected = line.split("=", 1)[1].strip().strip('\"').strip("'")
                    break
        except OSError:
            pass
    supplied = handler.headers.get("X-Mix-Agent-Token", "").strip()
    return bool(expected) and supplied == expected


def _agent_id(handler) -> str:
    return handler.headers.get("X-Mix-Agent-Id", "local-agent")[:100] or "local-agent"


def _send_file(handler, path: Path, content_type: str, filename: str) -> None:
    handler.send_response(200)
    handler.send_header("Content-Type", content_type)
    handler.send_header("Content-Length", str(path.stat().st_size))
    # http.server headers are latin-1 encoded; RFC 5987 keeps Chinese names
    # from raising UnicodeEncodeError and closing the download connection.
    safe_name = Path(filename).name or "audio"
    ascii_name = "audio" + Path(safe_name).suffix.lower()
    encoded_name = quote(safe_name, safe="")
    handler.send_header(
        "Content-Disposition",
        f'attachment; filename="{ascii_name}"; filename*=UTF-8\'\'{encoded_name}',
    )
    handler._write_cors_headers()
    handler.end_headers()
    with path.open("rb") as file:
        while chunk := file.read(64 * 1024):
            handler.wfile.write(chunk)


def _upload(handler) -> None:
    maximum = int(os.environ.get("MIX_MAX_FILE_SIZE_MB", "100")) * 1024 * 1024 + 256 * 1024
    body = _read_body(handler, maximum)
    parts = parse_multipart(handler.headers.get("Content-Type", ""), body)
    file_part = (parts.get("file") or [{}])[0]
    role = ((parts.get("role") or [{}])[0].get("content", b"").decode("utf-8", errors="replace").strip())
    if role not in ALLOWED_ROLES:
        raise UploadError("请选择有效的音频轨道类型")
    content = file_part.get("content", b"")
    if not content:
        raise UploadError("未收到音频文件")
    limit = int(os.environ.get("MIX_MAX_FILE_SIZE_MB", "100")) * 1024 * 1024
    if len(content) > limit:
        raise UploadError(f"文件过大，单个文件不能超过 {os.environ.get('MIX_MAX_FILE_SIZE_MB', '100')} MB")
    temporary = store.STAGING_DIR / f"inspect_{os.urandom(8).hex()}"
    temporary.write_bytes(content)
    try:
        metadata = inspect_audio(temporary)
        record = store.stage_upload(file_part.get("filename", "audio"), metadata["format"], content, metadata)
    finally:
        temporary.unlink(missing_ok=True)
    handler._json(201, {"file": {key: value for key, value in record.items() if key != "path"}, "role": role})


def _create_job(handler) -> None:
    payload = _json_body(handler)
    uploads = payload.get("uploads")
    if not isinstance(uploads, list):
        raise UploadError("请先上传音频文件")
    request = {
        "user_prompt": str(payload.get("user_prompt", ""))[:2000],
        "genre_hint": str(payload.get("genre_hint", "AI 自动判断"))[:60],
    }
    plan = planner.create_plan(request["user_prompt"], request["genre_hint"])
    job = store.create_job(uploads, request, plan)
    handler._json(201, {"job": public_job(job)})


def _agent_next(handler) -> None:
    if not _agent_allowed(handler):
        handler._json(401, {"error": "Agent token 无效"})
        return
    job = store.claim_next(_agent_id(handler))
    if not job:
        handler._json(204, {})
        return
    agent_job = public_job(job)
    for item in agent_job["inputs"]:
        item["download_path"] = f"/api/mixing/jobs/{job['job_id']}/files/{item['file_id']}"
    agent_job["agent"] = job["agent"]
    handler._json(200, {"job": agent_job})


def _agent_update(handler, job_id: str, action: str) -> None:
    if not _agent_allowed(handler):
        handler._json(401, {"error": "Agent token 无效"})
        return
    agent_id = _agent_id(handler)
    try:
        if action == "heartbeat":
            job = store.heartbeat(job_id, agent_id)
        elif action == "progress":
            payload = _json_body(handler)
            store.heartbeat(job_id, agent_id)
            job = store.update_job(job_id, payload.get("status"), payload.get("message"))
        elif action == "fail":
            payload = _json_body(handler)
            store.heartbeat(job_id, agent_id)
            step = str(payload.get("step", ""))[:80] or "unknown"
            error = str(payload.get("error", ""))[:1000] or "Local Agent 执行失败"
            job = store.update_job(job_id, "failed", f"[{step}] {error}", error=error, failure_step=step)
        else:  # result
            maximum = int(os.environ.get("MIX_MAX_FILE_SIZE_MB", "100")) * 1024 * 1024 + 256 * 1024
            body = _read_body(handler, maximum)
            parts = parse_multipart(handler.headers.get("Content-Type", ""), body)
            file_part = (parts.get("file") or [{}])[0]
            content = file_part.get("content", b"")
            temporary = store.RESULTS_DIR / f"inspect_{os.urandom(8).hex()}"
            temporary.write_bytes(content)
            try:
                metadata = inspect_audio(temporary)
                if metadata["format"] not in {"wav", "mp3"}:
                    raise UploadError("Local Agent 最终结果仅支持 WAV 或 MP3")
            finally:
                temporary.unlink(missing_ok=True)
            store.heartbeat(job_id, agent_id)
            execution_mode = handler.headers.get("X-Mix-Execution-Mode", "studio_one").strip()[:40] or "studio_one"
            job = store.save_result(job_id, file_part.get("filename", "zhisheng_mix.wav"), content, metadata, execution_mode)
        handler._json(200, {"job": public_job(job)})
    except (KeyError, PermissionError) as exc:
        handler._json(404 if isinstance(exc, KeyError) else 403, {"error": str(exc)})
    except (UploadError, ValueError) as exc:
        handler._json(400, {"error": str(exc)})


def handle(handler, method: str, request_path: str) -> bool:
    """Handle mixing routes and return whether the request belonged to this module."""
    if not request_path.startswith("/api/mixing/"):
        return False
    try:
        if method == "POST" and request_path == "/api/mixing/uploads":
            _upload(handler)
        elif method == "POST" and request_path == "/api/mixing/jobs":
            _create_job(handler)
        elif method == "GET" and request_path.startswith("/api/mixing/jobs/"):
            parts = request_path.strip("/").split("/")
            if len(parts) == 4:
                job = store.get_job(parts[3])
                if not job:
                    handler._json(404, {"error": "任务不存在"})
                else:
                    handler._json(200, {"job": public_job(job)})
            elif len(parts) == 6 and parts[4] == "files":
                job = store.get_job(parts[3])
                item = next((entry for entry in (job or {}).get("inputs", []) if entry["file_id"] == parts[5]), None)
                if not item or not Path(item["path"]).is_file():
                    handler._json(404, {"error": "音频文件不存在"})
                else:
                    _send_file(handler, Path(item["path"]), "audio/wav" if item["format"] == "wav" else "audio/mpeg", item["display_name"])
            elif len(parts) == 5 and parts[4] == "result":
                job = store.get_job(parts[3])
                result = (job or {}).get("result", {})
                path = Path(result.get("path") or "")
                if not result.get("file_id") or not path.is_file():
                    handler._json(404, {"error": "混音结果尚未生成"})
                else:
                    content_type = "audio/mpeg" if result.get("format") == "mp3" else "audio/wav"
                    fallback = "zhisheng_mix.mp3" if result.get("format") == "mp3" else "zhisheng_mix.wav"
                    _send_file(handler, path, content_type, result.get("display_name") or fallback)
            else:
                handler._json(404, {"error": "Not found"})
        elif method == "GET" and request_path == "/api/mixing/agent/jobs/next":
            _agent_next(handler)
        elif method == "POST" and request_path.startswith("/api/mixing/agent/jobs/"):
            pieces = request_path.strip("/").split("/")
            if len(pieces) != 6 or pieces[5] not in {"heartbeat", "progress", "result", "fail"}:
                handler._json(404, {"error": "Not found"})
            else:
                _agent_update(handler, pieces[4], pieces[5])
        else:
            handler._json(404, {"error": "Not found"})
    except UploadError as exc:
        handler._json(400, {"error": str(exc)})
    return True
