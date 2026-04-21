from fastapi.testclient import TestClient

from memory_transfer_server.main import create_app


def sample_bundle() -> dict[str, object]:
    return {
        "version": "1.0",
        "source_agent": "unit-test-source",
        "exported_at": "2026-04-21T00:00:00Z",
        "memories": [
            {
                "id": "mem_1",
                "type": "preference",
                "title": "Style preference",
                "content": "Prefer short answers.",
                "tags": ["style"],
                "transferable": True,
                "sensitivity": "low",
            }
        ],
    }


def test_create_transfer_returns_identifiers() -> None:
    app = create_app()
    with TestClient(app) as client:
        response = client.post(
            "/transfer/create",
            json={"bundle": sample_bundle(), "ttl_seconds": 3600, "consume_once": True},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["transfer_id"].startswith("tr_")
    assert len(payload["short_code"]) == 6
    assert payload["qr_payload"].startswith("memory-transfer://fetch")
    assert payload["consume_once"] is True
