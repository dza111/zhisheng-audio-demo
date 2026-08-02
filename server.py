from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


class SpaHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        requested = Path(self.translate_path(self.path)).resolve()
        if not requested.exists() and "." not in Path(self.path).name:
            self.path = "/index.html"
        return super().do_GET()


if __name__ == "__main__":
    host, port = "127.0.0.1", 4173
    print(f"Zhisheng Audio Demo: http://{host}:{port}")
    ThreadingHTTPServer((host, port), SpaHandler).serve_forever()
