import json
import subprocess
import sys
from pathlib import Path


def test_export_memory_filters_temporary(tmp_path: Path) -> None:
    source = tmp_path / "source.json"
    source.write_text(
        json.dumps(
            {
                "version": "1.0",
                "source_agent": "test",
                "exported_at": "2026-04-21T00:00:00Z",
                "memories": [
                    {
                        "id": "keep_1",
                        "type": "preference",
                        "title": "Keep me",
                        "content": "Stable preference",
                        "tags": [],
                        "transferable": True,
                        "sensitivity": "low",
                    },
                    {
                        "id": "drop_1",
                        "type": "temporary",
                        "title": "Drop me",
                        "content": "Ephemeral cache",
                        "tags": [],
                        "transferable": True,
                        "sensitivity": "low",
                    },
                ],
            }
        ),
        encoding="utf-8",
    )

    script = Path(__file__).resolve().parents[1] / "scripts/export_memory.py"
    result = subprocess.run(
        [sys.executable, str(script), "--source", str(source)],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert len(payload["memories"]) == 1
    assert payload["memories"][0]["id"] == "keep_1"
