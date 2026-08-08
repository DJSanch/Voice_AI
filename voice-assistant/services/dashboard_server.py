"""Local-only web server for Astra's Command Center."""

from __future__ import annotations

import json
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlparse

from services.dashboard import dashboard_state, enqueue_dashboard_command


PROJECT_DIR = Path(__file__).resolve().parent.parent
DASHBOARD_DIR = PROJECT_DIR / "dashboard"


class DashboardRequestHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path: str) -> str:
        clean_path = urlparse(path).path
        if clean_path in {"/", "/index.html"}:
            return str(DASHBOARD_DIR / "index.html")
        if clean_path in {"/app.js", "/styles.css", "/state.json"}:
            return str(DASHBOARD_DIR / clean_path.lstrip("/"))
        if clean_path.startswith("/data/"):
            data_dir = (PROJECT_DIR / "data").resolve()
            requested_file = (PROJECT_DIR / clean_path.lstrip("/")).resolve()
            if requested_file.is_relative_to(data_dir):
                return str(requested_file)
        return str(DASHBOARD_DIR / "index.html")

    def do_GET(self) -> None:
        if urlparse(self.path).path == "/api/state":
            self._send_json(HTTPStatus.OK, dashboard_state._read())
            return
        super().do_GET()

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/commands":
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length))
            command = payload.get("command", "").strip()
        except (ValueError, json.JSONDecodeError):
            command = ""
        if not command or len(command) > 500:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "A command is required."})
            return
        if not enqueue_dashboard_command(command):
            self._send_json(
                HTTPStatus.CONFLICT,
                {"error": "A morning briefing is already in progress."},
            )
            return
        self._send_json(HTTPStatus.ACCEPTED, {"accepted": True})

    def _send_json(self, status: HTTPStatus, payload: dict) -> None:
        data = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *_: object) -> None:
        return


def start_dashboard_server(port: int = 8080) -> None:
    """Start the local Command Center once, without blocking Astra."""
    try:
        server = ThreadingHTTPServer(("127.0.0.1", port), DashboardRequestHandler)
    except OSError:
        print(f"Astra Command Center could not start on port {port}.")
        return
    Thread(target=server.serve_forever, daemon=True, name="astra-dashboard").start()
    print(f"Astra Command Center: http://localhost:{port}")
