import json
import subprocess
import sys
from pathlib import Path


def test_import_memory_upsert(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle.json"
    target = tmp_path / "target.json"

    bundle.write_text(
        json.dumps(
            {
                "version": "1.0",
                "source_agent": "test",
                "exported_at": "2026-04-21T00:00:00Z",
                "memories": [
                    {
                        "id": "mem_1",
                        "type": "profile",
                        "title": "New profile",
                        "content": "Updated content",
                        "tags": [],
                        "transferable": True,
                        "sensitivity": "low",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    target.write_text(
        json.dumps(
            {
                "memories": [
                    {
                        "id": "mem_1",
                        "type": "profile",
                        "title": "Old profile",
                        "content": "Old content",
                        "tags": [],
                        "transferable": True,
                        "sensitivity": "low",
                    },
                    {
                        "id": "mem_2",
                        "type": "workflow",
                        "title": "Keep workflow",
                        "content": "Keep this",
                        "tags": [],
                        "transferable": True,
                        "sensitivity": "low",
                    },
                ]
            }
        ),
        encoding="utf-8",
    )

    script = Path(__file__).resolve().parents[1] / "scripts/import_memory.py"
    subprocess.run(
        [sys.executable, str(script), "--bundle", str(bundle), "--target", str(target), "--mode", "upsert"],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(target.read_text(encoding="utf-8"))
    assert len(payload["memories"]) == 2
    assert payload["memories"][0]["title"] == "New profile"
