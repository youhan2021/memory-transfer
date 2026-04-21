import json
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path


class _Handler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:  # noqa: N802
        if self.path == "/transfer/create":
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length)
            payload = json.loads(body.decode("utf-8"))
            memories = payload["bundle"]["memories"]
            response = {
                "transfer_id": "tr_test",
                "expires_at": "2026-04-21T01:00:00Z",
                "short_code": "mango-river-27",
                "confirm_phrase": "silver bamboo",
                "memory_count": len(memories),
            }
            encoded = json.dumps(response).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)
            return

        if self.path == "/transfer/lookup":
            encoded = json.dumps(
                {
                    "transfer_id": "tr_test",
                    "short_code": "mango-river-27",
                    "status": "pending",
                    "preview": {
                        "source_agent": "hermes",
                        "exported_at": "2026-04-21T00:00:00Z",
                        "expires_at": "2026-04-21T01:00:00Z",
                        "memory_count": 2,
                        "memory_type_counts": {"preference": 1, "workflow": 1},
                        "requires_confirm_phrase": True,
                    },
                }
            ).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)
            return

        if self.path != "/transfer/confirm-import":
            self.send_response(404)
            self.end_headers()
            return
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length)
        payload = json.loads(body.decode("utf-8"))
        response = {
            "transfer_id": "tr_test",
            "short_code": payload["short_code"],
            "status": "consumed",
            "import_mode": payload["import_mode"],
            "consumed_at": "2026-04-21T00:10:00Z",
            "bundle": {
                "version": "1.0",
                "source_agent": "hermes",
                "exported_at": "2026-04-21T00:00:00Z",
                "memories": [
                    {
                        "id": "mem_1",
                        "type": "preference",
                        "title": "Imported preference",
                        "content": "Keep answers concise.",
                        "tags": ["style"],
                        "transferable": True,
                        "sensitivity": "low",
                    }
                ],
            },
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
        script = Path(__file__).resolve().parents[2] / "skills/memory-transfer/scripts/create_transfer.py"
        env = {"MEMORY_TRANSFER_SERVER_URL": f"http://127.0.0.1:{server.server_port}/"}
        result = subprocess.run(
            [sys.executable, str(script), "--source", str(source)],
            check=True,
            capture_output=True,
            text=True,
            env=env,
        )
    finally:
        server.shutdown()
        thread.join(timeout=2)

    assert "Transfer ready." in result.stdout
    assert "Code: mango-river-27" in result.stdout
    assert "Confirm phrase: silver bamboo" in result.stdout
    assert "Transfer ID: tr_test" in result.stdout
    assert "Send this to the target agent:" in result.stdout
    assert "短码是 mango-river-27" in result.stdout
    assert "python3" not in result.stdout


def test_create_transfer_json_mode(tmp_path: Path) -> None:
    source = tmp_path / "note.md"
    source.write_text("用户偏好简洁说明和短编码分享。", encoding="utf-8")

    server = HTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        script = Path(__file__).resolve().parents[2] / "skills/memory-transfer/scripts/create_transfer.py"
        env = {"MEMORY_TRANSFER_SERVER_URL": f"http://127.0.0.1:{server.server_port}/"}
        result = subprocess.run(
            [
                sys.executable,
                str(script),
                "--source",
                str(source),
                "--format",
                "json",
            ],
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
    assert payload["short_code"] == "mango-river-27"
    assert payload["confirm_phrase"] == "silver bamboo"


def test_lookup_transfer_prompt_mode(tmp_path: Path) -> None:
    server = HTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        script = Path(__file__).resolve().parents[2] / "skills/memory-transfer/scripts/lookup_transfer.py"
        env = {"MEMORY_TRANSFER_SERVER_URL": f"http://127.0.0.1:{server.server_port}/"}
        result = subprocess.run(
            [sys.executable, str(script), "--short-code", "mango-river-27"],
            check=True,
            capture_output=True,
            text=True,
            env=env,
        )
    finally:
        server.shutdown()
        thread.join(timeout=2)

    assert "Found a memory bundle from hermes." in result.stdout
    assert "- 1 preference" in result.stdout
    assert "To continue, enter the confirm phrase." in result.stdout


def test_confirm_import_prompt_mode(tmp_path: Path) -> None:
    target = tmp_path / "target.json"
    server = HTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        script = Path(__file__).resolve().parents[2] / "skills/memory-transfer/scripts/confirm_import.py"
        env = {"MEMORY_TRANSFER_SERVER_URL": f"http://127.0.0.1:{server.server_port}/"}
        result = subprocess.run(
            [
                sys.executable,
                str(script),
                "--short-code",
                "mango-river-27",
                "--confirm-phrase",
                "silver bamboo",
                "--target",
                str(target),
                "--mode",
                "upsert",
            ],
            check=True,
            capture_output=True,
            text=True,
            env=env,
        )
    finally:
        server.shutdown()
        thread.join(timeout=2)

    payload = json.loads(target.read_text(encoding="utf-8"))
    assert len(payload["memories"]) == 1
    assert "Import completed." in result.stdout
    assert "Short Code: mango-river-27" in result.stdout
