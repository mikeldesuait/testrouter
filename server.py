#!/usr/bin/env python3
"""
Test Router - servidor local con guardado de progreso en disco.
Uso: python3 server.py
Abre: http://localhost:8000
"""
import http.server
import socketserver
import json
from pathlib import Path

PORT = 8000
BASE = Path(__file__).parent.resolve()
SAVE_DIR = BASE / "saves"
SAVE_DIR.mkdir(exist_ok=True)


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(BASE), **kwargs)

    def log_message(self, fmt, *args):
        print(f"[{self.log_date_time_string()}] {fmt % args}")

    def do_GET(self):
        if self.path == "/api/list":
            files = sorted(
                [f.name for f in SAVE_DIR.glob("*.json")],
                reverse=True
            )
            self.send_json(200, {"files": files})
            return
        super().do_GET()

    def do_POST(self):
        if self.path == "/api/save":
            try:
                length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(length)
                data = json.loads(body)
                name = data.get("filename") or "progress"
                name = "".join(c for c in name if c.isalnum() or c in "-_. ")
                if not name.endswith(".json"):
                    name += ".json"
                path = SAVE_DIR / name
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"💾 Guardado: {path.name}")
                self.send_json(200, {"ok": True, "file": path.name})
            except Exception as e:
                print(f"❌ Error guardando: {e}")
                self.send_json(500, {"ok": False, "error": str(e)})
        else:
            self.send_json(404, {"error": "not found"})

    def do_PUT(self):
        if self.path == "/api/load":
            try:
                length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(length)
                data = json.loads(body)
                name = data.get("filename", "")
                name = "".join(c for c in name if c.isalnum() or c in "-_. ")
                path = SAVE_DIR / name
                if not path.exists():
                    self.send_json(404, {"ok": False, "error": "no existe"})
                    return
                with open(path, "r", encoding="utf-8") as f:
                    content = json.load(f)
                print(f"📥 Cargado: {path.name}")
                self.send_json(200, {"ok": True, "data": content})
            except Exception as e:
                print(f"❌ Error cargando: {e}")
                self.send_json(500, {"ok": False, "error": str(e)})
        else:
            self.send_json(404, {"error": "not found"})

    def send_json(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()


if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("=" * 60)
        print(f"🚀 Test Router en:  http://localhost:{PORT}")
        print(f"📁 Carpeta:         {BASE}")
        print(f"💾 Guardados en:    {SAVE_DIR}")
        print("=" * 60)
        print("Ctrl+C para detener.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Servidor detenido.")
