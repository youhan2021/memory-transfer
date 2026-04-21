import json
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path


class _Handler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/transfer/create":
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length)
        payload = json.loads(body.decode("utf-8"))
        memories = payload["bundle"]["memories"]
        response = {
            "transfer_id": "tr_test",
            "expires_at": "2026-04-21T01:00:00Z",
            "short_code": "ABC123",
            "qr_payload": "memory-transfer://fetch?transfer_id=tr_test&code=ABC123",
            "consume_once": payload["consume_once"],
            "memory_count": len(memories),
        }
        encoded = json.dumps(response).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return


def test_create_transfer_from_markdown(tmp_path: Path) -> None:
    source = tmp_path / "note.md"
    source.write_text("用户偏好简洁说明和短编码分享。", encoding="utf-8")

    server = HTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        script = Path(__file__).resolve().parents[1] / "scripts/create_transfer.py"
        env = {"MEMORY_TRANSFER_SERVER_URL": f"http://127.0.0.1:{server.server_port}/"}
        result = subprocess.run(
            [sys.executable, str(script), "--source", str(source), "--output-kind", "short"],
            check=True,
            capture_output=True,
            text=True,
            env=env,
        )
    finally:
        server.shutdown()
        thread.join(timeout=2)

    payload = json.loads(result.stdout)
    assert payload["transfer_id"] == "tr_test"
    assert payload["short_code"] == "ABC123"
    assert "qr_payload" not in payload
    assert payload["next_commands"]["import_by_short_code"].startswith(
        "python scripts/fetch_transfer.py --short-code ABC123"
    )
