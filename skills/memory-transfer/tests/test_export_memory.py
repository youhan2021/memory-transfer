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
    assert len(payload["memories"]) == 2
    assert {item["id"] for item in payload["memories"]} == {"keep_1", "drop_1"}


def test_export_memory_generates_bundle_from_markdown(tmp_path: Path) -> None:
    source = tmp_path / "2026-04-18-moyu-threebody.md"
    source.write_text(
        "摸鱼记录：今天继续读三体，偏好安静阅读环境，后续可以继续跟进阅读进度。",
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
    assert payload["source_agent"] == "2026-04-18-moyu-threebody"
    assert len(payload["memories"]) == 1
    assert payload["memories"][0]["title"] == "2026 04 18 moyu threebody"
    assert payload["memories"][0]["transferable"] is True


def test_export_memory_does_not_drop_negative_tmp_reference(tmp_path: Path) -> None:
    source = tmp_path / "MEMORY.md"
    source.write_text(
        "这里记录的是稳定记忆，不是 /tmp/ 目录，也不是临时缓存。",
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
    assert payload["memories"][0]["transferable"] is True


def test_export_memory_only_filters_when_types_is_explicit(tmp_path: Path) -> None:
    source = tmp_path / "source.json"
    source.write_text(
        json.dumps(
            {
                "version": "1.0",
                "source_agent": "test",
                "exported_at": "2026-04-21T00:00:00Z",
                "memories": [
                    {
                        "id": "pref_1",
                        "type": "preference",
                        "title": "Keep",
                        "content": "Stable preference",
                        "tags": [],
                        "transferable": True,
                        "sensitivity": "low",
                    },
                    {
                        "id": "tmp_1",
                        "type": "temporary",
                        "title": "Also keep by default",
                        "content": "Temporary note",
                        "tags": [],
                        "transferable": False,
                        "sensitivity": "low",
                    },
                ],
            }
        ),
        encoding="utf-8",
    )

    script = Path(__file__).resolve().parents[1] / "scripts/export_memory.py"
    default_result = subprocess.run(
        [sys.executable, str(script), "--source", str(source)],
        check=True,
        capture_output=True,
        text=True,
    )
    typed_result = subprocess.run(
        [sys.executable, str(script), "--source", str(source), "--types", "preference"],
        check=True,
        capture_output=True,
        text=True,
    )

    default_payload = json.loads(default_result.stdout)
    typed_payload = json.loads(typed_result.stdout)
    assert len(default_payload["memories"]) == 2
    assert len(typed_payload["memories"]) == 1
    assert typed_payload["memories"][0]["id"] == "pref_1"
