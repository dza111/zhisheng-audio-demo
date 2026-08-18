import json
import os
import urllib.error
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"


class SpaHandler(SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _cors_origin(self):
        allowed = os.environ.get("ALLOWED_ORIGINS", "*")
        request_origin = self.headers.get("Origin", "")
        if allowed == "*":
            return "*"
        return request_origin if request_origin in {x.strip() for x in allowed.split(",")} else allowed.split(",")[0].strip()

    def _json(self, status, payload):
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Access-Control-Allow-Origin", self._cors_origin())
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(raw)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", self._cors_origin())
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Max-Age", "86400")
        self.end_headers()

    def do_POST(self):
        if self.path != "/api/chat":
            self._json(404, {"error": "Not found"})
            return

        api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
        if not api_key:
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
        self.send_header("Access-Control-Allow-Origin", self._cors_origin())
        self.end_headers()
        try:
            tail = b""
            while chunk := upstream.read(4096):
                self.wfile.write(chunk)
                self.wfile.flush()
                tail = (tail + chunk)[-128:]
                if b"data: [DONE]" in tail:
                    break
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            upstream.close()

    def do_GET(self):
        requested = Path(self.translate_path(self.path)).resolve()
        if not requested.exists() and "." not in Path(self.path).name:
            self.path = "/index.html"
        return super().do_GET()


if __name__ == "__main__":
    host, port = os.environ.get("HOST", "127.0.0.1"), int(os.environ.get("PORT", "4173"))
    print(f"Zhisheng Audio Demo: http://{host}:{port}")
    ThreadingHTTPServer((host, port), SpaHandler).serve_forever()
