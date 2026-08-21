from __future__ import annotations

import json
import mimetypes
import os
import sys
import threading
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path


AGENT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(AGENT_DIR))
from studio_one_adapter import get_adapter  # noqa: E402


def load_dotenv(path: Path) -> dict[str, str]:
    """Read simple KEY=VALUE entries without overriding process environment."""
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        if key:
            values[key] = value
    return values


def load_config() -> dict:
    config_path = Path(os.environ.get("MIX_AGENT_CONFIG", AGENT_DIR / "config.json"))
    config = json.loads(config_path.read_text(encoding="utf-8")) if config_path.is_file() else {}
    dotenv = load_dotenv(AGENT_DIR / ".env")
    config["server_url"] = os.environ.get("MIX_SERVER_URL", dotenv.get("MIX_SERVER_URL", config.get("server_url", ""))).rstrip("/")
    config["token"] = os.environ.get("MIX_AGENT_TOKEN", dotenv.get("MIX_AGENT_TOKEN", config.get("token", "")))
    config["agent_id"] = os.environ.get("MIX_AGENT_ID", config.get("agent_id", "zhisheng-local-agent"))
    config["work_dir"] = os.environ.get("MIX_WORK_DIR", config.get("work_dir", str(Path.home() / "ZhishengMixJobs")))
    if not config["server_url"] or not config["token"]:
        raise RuntimeError("请配置 MIX_SERVER_URL 和 MIX_AGENT_TOKEN")
    return config


class ApiClient:
    def __init__(self, config: dict):
        self.base = config["server_url"]
        self.headers = {"X-Mix-Agent-Token": config["token"], "X-Mix-Agent-Id": config["agent_id"]}

    def request(self, method: str, path: str, payload: dict | None = None) -> tuple[int, bytes]:
        headers = dict(self.headers)
        data = None
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        request = urllib.request.Request(self.base + path, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                return response.status, response.read()
        except urllib.error.HTTPError as exc:
            return exc.code, exc.read()

    def download(self, path: str, destination: Path) -> None:
        request = urllib.request.Request(self.base + path, headers=self.headers)
        with urllib.request.urlopen(request, timeout=300) as response, destination.open("wb") as output:
            while chunk := response.read(64 * 1024):
                output.write(chunk)

    def upload_audio(self, path: str, audio_path: Path, execution_mode: str = "studio_one") -> tuple[int, bytes]:
        boundary = f"----ZhishengAgent{uuid.uuid4().hex}"
        content = audio_path.read_bytes()
        name = audio_path.name.encode("utf-8")
        body = b"".join([
            f"--{boundary}\r\n".encode(),
            b'Content-Disposition: form-data; name="file"; filename="' + name + b'"\r\n',
            (b"Content-Type: audio/mpeg\r\n\r\n" if audio_path.suffix.lower() == ".mp3" else b"Content-Type: audio/wav\r\n\r\n"), content, b"\r\n",
            f"--{boundary}--\r\n".encode(),
        ])
        headers = {
            **self.headers,
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "X-Mix-Execution-Mode": execution_mode,
        }
        request = urllib.request.Request(self.base + path, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=300) as response:
                return response.status, response.read()
        except urllib.error.HTTPError as exc:
            return exc.code, exc.read()


def process_job(client: ApiClient, adapter, config: dict, job: dict) -> None:
    job_id = job["job_id"]
    workspace = Path(config["work_dir"]).expanduser() / job_id
    input_dir = workspace / "inputs"
    input_dir.mkdir(parents=True, exist_ok=True)

    current_step = "preparing"

    def report(status: str, message: str) -> None:
        nonlocal current_step
        current_step = status
        print(f"[{job_id}] {status}: {message}", flush=True)
        client.request("POST", f"/api/mixing/agent/jobs/{job_id}/progress", {"status": status, "message": message})

    heartbeat_stop = threading.Event()

    def heartbeat_loop() -> None:
        while not heartbeat_stop.wait(20):
            client.request("POST", f"/api/mixing/agent/jobs/{job_id}/heartbeat", {})

    heartbeat_thread = threading.Thread(target=heartbeat_loop, daemon=True)
    heartbeat_thread.start()
    try:
        report("preparing", "Local Agent 正在下载音频并准备 Studio One 工作目录")
        for item in job["inputs"]:
            extension = item["format"]
            destination = input_dir / f"{item['role']}_{item['file_id']}.{extension}"
            client.download(item["download_path"], destination)
            item["local_path"] = str(destination)
        result = adapter.process(job, workspace, report)
        report("uploading_result", "Local Agent 正在上传最终 MP3/WAV")
        status, response = client.upload_audio(
            f"/api/mixing/agent/jobs/{job_id}/result",
            result.output_path,
            result.execution_mode,
        )
        if status not in {200, 201}:
            raise RuntimeError(response.decode("utf-8", errors="replace")[:500])
    except Exception as exc:
        print(f"[{job_id}] STUDIO_ONE_MIX_FAILED: {exc}", flush=True)
        client.request("POST", f"/api/mixing/agent/jobs/{job_id}/fail", {"step": current_step, "error": str(exc)})
    finally:
        heartbeat_stop.set()
        heartbeat_thread.join(timeout=1)


def main() -> None:
    config = load_config()
    work_dir = Path(config["work_dir"]).expanduser()
    work_dir.mkdir(parents=True, exist_ok=True)
    client = ApiClient(config)
    adapter = get_adapter(config.get("adapter", "manual"), config)
    health = adapter.healthcheck()
    print(f"Zhisheng Local Agent: {health.message}")
    if not health.ready:
        print("修正 config.json 后重新启动 Agent。")
        return
    while True:
        status, raw = client.request("GET", "/api/mixing/agent/jobs/next")
        if status == 200 and raw:
            payload = json.loads(raw.decode("utf-8"))
            if payload.get("job"):
                process_job(client, adapter, config, payload["job"])
                continue
        elif status not in {204, 200}:
            print(f"获取任务失败：{status} {raw.decode('utf-8', errors='replace')[:200]}")
        time.sleep(max(3, int(config.get("poll_seconds", 5))))


if __name__ == "__main__":
    main()
