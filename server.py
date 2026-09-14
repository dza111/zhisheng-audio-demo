import json
import os
import threading
import time
import http.client
import urllib.error
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse


def _load_local_env() -> None:
    """Load ignored local secrets without overriding deployment environment variables."""
    project_root = Path(__file__).resolve().parent
    allowed_by_file = {
        project_root / ".env": {
            "DEEPSEEK_API_KEY", "DEEPSEEK_MODEL", "SYSTEM_PROMPT",
            "ALLOWED_ORIGINS", "RATE_LIMIT", "RATE_WINDOW_SECONDS",
        },
        project_root / "local_agent" / ".env": {"MIX_AGENT_TOKEN"},
    }
    for env_path, allowed_keys in allowed_by_file.items():
        if not env_path.is_file():
            continue
        try:
            lines = env_path.read_text(encoding="utf-8-sig").splitlines()
        except OSError:
            continue
        for raw_line in lines:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key in allowed_keys and value:
                os.environ.setdefault(key, value)


_load_local_env()

from mixing.api import handle as handle_mixing_request
from site_knowledge import build_ai_context, public_resources


DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"
DEFAULT_LOCAL_CHAT_FALLBACK_URL = (
    "https://zhisheng-ai-298879-11-1470821727.sh.run.tcloudbase.com/api/chat"
)
RATE_WINDOW_SECONDS = int(os.environ.get("RATE_WINDOW_SECONDS", "60"))
RATE_LIMIT = int(os.environ.get("RATE_LIMIT", "15"))
RATE_BUCKETS = {}
RATE_LOCK = threading.Lock()
DEFAULT_SYSTEM_PROMPT = os.environ.get(
    "SYSTEM_PROMPT",
    "You are a helpful assistant. Reply in the user's language. Use clear structure: "
    "put each numbered point or bullet on its own line, keep paragraphs short, and use blank lines "
    "between separate sections. Do not use tables unless specifically requested.",
)


class SpaHandler(SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def end_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "SAMEORIGIN")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        self.send_header("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        if urlparse(self.path).path.endswith((".js", ".css", ".html")):
            self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def _allowed_origins(self):
        configured = os.environ.get("ALLOWED_ORIGINS", "").strip()
        if configured:
            return {item.strip() for item in configured.split(",") if item.strip()}
        host = self.headers.get("Host", "")
        return {f"https://{host}", f"http://{host}"} if host else set()

    def _origin_allowed(self):
        origin = self.headers.get("Origin")
        if not origin:
            return True
        allowed = self._allowed_origins()
        return "*" in allowed or origin in allowed

    def _cors_origin(self):
        origin = self.headers.get("Origin", "")
        if not origin or not self._origin_allowed():
            return None
        return "*" if "*" in self._allowed_origins() else origin

    def _write_cors_headers(self):
        origin = self._cors_origin()
        if origin:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")

    def _client_ip(self):
        forwarded = self.headers.get("X-Forwarded-For", "")
        return forwarded.split(",")[0].strip() if forwarded else self.client_address[0]

    def _rate_limited(self):
        now = time.monotonic()
        client = self._client_ip()
        with RATE_LOCK:
            timestamps = [stamp for stamp in RATE_BUCKETS.get(client, []) if now - stamp < RATE_WINDOW_SECONDS]
            if len(timestamps) >= RATE_LIMIT:
                RATE_BUCKETS[client] = timestamps
                return True
            timestamps.append(now)
            RATE_BUCKETS[client] = timestamps
            return False

    def _json(self, status, payload):
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self._write_cors_headers()
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(raw)

    def do_OPTIONS(self):
        if not self._origin_allowed():
            self._json(403, {"error": "Origin is not allowed"})
            return
        self.send_response(204)
        self._write_cors_headers()
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Max-Age", "86400")
        self.end_headers()

    def do_POST(self):
        request_path = unquote(urlparse(self.path).path)
        if request_path.startswith("/api/mixing/"):
            if not self._origin_allowed():
                self._json(403, {"error": "Origin is not allowed"})
                return
            if self._rate_limited():
                self._json(429, {"error": "Too many requests. Please try again shortly."})
                return
            handle_mixing_request(self, "POST", request_path)
            return
        if self.path != "/api/chat":
            self._json(404, {"error": "Not found"})
            return
        if not self._origin_allowed():
            self._json(403, {"error": "Origin is not allowed"})
            return
        if self._rate_limited():
            self._json(429, {"error": "Too many requests. Please try again shortly."})
            return

        api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
        if not api_key:
            host = self.headers.get("Host", "").split(":", 1)[0].lower()
            fallback_url = os.environ.get(
                "LOCAL_CHAT_FALLBACK_URL", DEFAULT_LOCAL_CHAT_FALLBACK_URL
            ).strip()
            if fallback_url and host in {"127.0.0.1", "localhost", "::1"}:
                self._proxy_local_chat(fallback_url)
                return
            self._json(500, {"error": "Server is missing DEEPSEEK_API_KEY"})
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 256 * 1024:
                raise ValueError("Request body is empty or too large")
            body = json.loads(self.rfile.read(length).decode("utf-8"))
            messages = body.get("messages")
            if not isinstance(messages, list) or not messages:
                raise ValueError("messages must be a non-empty array")
            clean_messages = []
            for item in messages[-30:]:
                if item.get("role") not in {"system", "user", "assistant"}:
                    raise ValueError("Unsupported message role")
                content = str(item.get("content", ""))[:12000]
                clean_messages.append({"role": item["role"], "content": content})
        except (ValueError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            self._json(400, {"error": str(exc)})
            return

        if not any(item["role"] == "system" for item in clean_messages):
            latest_query = next(
                (item["content"] for item in reversed(clean_messages) if item["role"] == "user"),
                "",
            )
            resource_context, _ = build_ai_context(latest_query)
            clean_messages.insert(0, {
                "role": "system",
                "content": f"{DEFAULT_SYSTEM_PROMPT}\n\n{resource_context}",
            })

        request_body = json.dumps({
            "model": os.environ.get("DEEPSEEK_MODEL", "deepseek-chat"),
            "messages": clean_messages,
            "stream": True,
            "temperature": 0.7,
        }).encode("utf-8")
        request = urllib.request.Request(
            DEEPSEEK_URL,
            data=request_body,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "text/event-stream",
            },
            method="POST",
        )

        try:
            upstream = urllib.request.urlopen(request, timeout=120)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:2000]
            self._json(exc.code if 400 <= exc.code < 600 else 502, {"error": detail or "DeepSeek request failed"})
            return
        except urllib.error.URLError as exc:
            self._json(502, {"error": f"Unable to reach DeepSeek: {exc.reason}"})
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache, no-transform")
        self.send_header("Connection", "keep-alive")
        self.send_header("X-Accel-Buffering", "no")
        self._write_cors_headers()
        self.end_headers()
        try:
            # SSE is line-oriented. readline() forwards tokens immediately instead of
            # waiting for a large buffered read to fill up.
            while line := upstream.readline():
                self.wfile.write(line)
                self.wfile.flush()
                if line.strip() == b"data: [DONE]":
                    self.close_connection = True
                    break
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _proxy_local_chat(self, fallback_url: str) -> None:
        """Use the deployed AI backend for local previews when no local key exists."""
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 256 * 1024:
                raise ValueError("Request body is empty or too large")
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            messages = payload.get("messages")
            if not isinstance(messages, list) or not messages:
                raise ValueError("messages must be a non-empty array")
            latest_query = next(
                (str(item.get("content", "")) for item in reversed(messages) if item.get("role") == "user"),
                "",
            )
            resource_context, _ = build_ai_context(latest_query)
            if not any(item.get("role") == "system" for item in messages):
                messages.insert(0, {
                    "role": "system",
                    "content": f"{DEFAULT_SYSTEM_PROMPT}\n\n{resource_context}",
                })
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        except (ValueError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            self._json(400, {"error": str(exc)})
            return

        request = urllib.request.Request(
            fallback_url,
            data=body,
            # CloudBase's edge protection can reject the default Python urllib
            # user agent intermittently.  This is still a server-to-server
            # request (no browser Origin is forwarded), but it is identified as
            # the local website preview instead of an anonymous script.
            headers={
                "Content-Type": "application/json",
                "Accept": "text/event-stream",
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/131.0 Safari/537.36 ZhishengAudioLocalPreview"
                ),
            },
            method="POST",
        )
        upstream = None
        last_error = ""
        for attempt in range(3):
            try:
                upstream = urllib.request.urlopen(request, timeout=120)
                break
            except urllib.error.HTTPError as exc:
                detail = exc.read().decode("utf-8", errors="replace")[:2000]
                # CloudBase can briefly return 5xx while waking a container,
                # and its edge occasionally replies 403/429 during a burst.
                # Retry the local preview request before exposing an error.
                if (exc.code == 403 or exc.code == 429 or 500 <= exc.code < 600) and attempt < 2:
                    last_error = detail or f"Cloud AI returned HTTP {exc.code}"
                    time.sleep(1 + attempt)
                    continue
                self._json(exc.code if 400 <= exc.code < 600 else 502, {"error": detail or "Cloud AI request failed"})
                return
            except (urllib.error.URLError, OSError, TimeoutError, http.client.HTTPException) as exc:
                last_error = str(getattr(exc, "reason", exc))
                if attempt < 2:
                    time.sleep(1 + attempt)
                    continue
        if upstream is None:
            self._json(502, {"error": f"Unable to reach deployed AI service after retry: {last_error}"})
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache, no-transform")
        self.send_header("Connection", "keep-alive")
        self.send_header("X-Accel-Buffering", "no")
        self._write_cors_headers()
        self.end_headers()
        try:
            while line := upstream.readline():
                self.wfile.write(line)
                self.wfile.flush()
                if line.strip() == b"data: [DONE]":
                    self.close_connection = True
                    break
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            upstream.close()

    def do_GET(self):
        parsed_url = urlparse(self.path)
        request_path = unquote(parsed_url.path)
        if request_path.startswith("/api/mixing/"):
            if not self._origin_allowed():
                self._json(403, {"error": "Origin is not allowed"})
                return
            handle_mixing_request(self, "GET", request_path)
            return
        path_parts = [part for part in Path(request_path).parts if part not in {"/", "\\"}]
        if any(part.startswith(".") for part in path_parts) or request_path.endswith((".py", ".env", ".key", ".pem")):
            self._json(404, {"error": "Not found"})
            return
        if request_path == "/api/health":
            self._json(200, {"status": "ok"})
            return
        if request_path == "/api/resources/search":
            if not self._origin_allowed():
                self._json(403, {"error": "Origin is not allowed"})
                return
            query = parse_qs(parsed_url.query).get("q", [""])[0].strip()[:500]
            self._json(200, {"resources": public_resources(query) if query else []})
            return
        requested = Path(self.translate_path(self.path)).resolve()
        if not requested.exists() and "." not in Path(self.path).name:
            self.path = "/index.html"
        return super().do_GET()


if __name__ == "__main__":
    # Keep the local server port aligned with local_agent/.env.
    host, port = os.environ.get("HOST", "127.0.0.1"), int(os.environ.get("PORT", "4175"))
    print(f"Zhisheng Audio Demo: http://{host}:{port}")
    ThreadingHTTPServer((host, port), SpaHandler).serve_forever()
