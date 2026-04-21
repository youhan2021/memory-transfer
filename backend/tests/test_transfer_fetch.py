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
                "type": "project_context",
                "title": "Install preference",
                "content": "One-command install is required.",
                "tags": ["install"],
                "transferable": True,
                "sensitivity": "medium",
            }
        ],
    }


def test_fetch_preview_and_full_bundle() -> None:
    app = create_app()
    with TestClient(app) as client:
        create_response = client.post(
            "/transfer/create",
            json={"bundle": sample_bundle(), "ttl_seconds": 3600, "consume_once": True},
        )
        transfer_id = create_response.json()["transfer_id"]

        preview_response = client.get(f"/transfer/{transfer_id}")
        full_response = client.get(f"/transfer/{transfer_id}?preview=false")

    assert preview_response.status_code == 200
    assert preview_response.json()["bundle"] is None
    assert preview_response.json()["preview"]["total_memories"] == 1

    assert full_response.status_code == 200
    assert full_response.json()["bundle"]["source_agent"] == "unit-test-source"


def test_fetch_by_short_code_aliases() -> None:
    app = create_app()
    with TestClient(app) as client:
        create_response = client.post(
            "/transfer/create",
            json={"bundle": sample_bundle(), "ttl_seconds": 3600, "consume_once": True},
        )
        payload = create_response.json()
        short_code = payload["short_code"]

        by_root = client.get(f"/transfer/{short_code}")
        by_code = client.get(f"/transfer/code/{short_code}")
        by_short = client.get(f"/transfer/short/{short_code}")
        by_post = client.post("/transfer/fetch", json={"code": short_code, "preview": True})

    assert by_root.status_code == 200
    assert by_root.json()["transfer_id"] == payload["transfer_id"]
    assert by_code.status_code == 200
    assert by_code.json()["transfer_id"] == payload["transfer_id"]
    assert by_short.status_code == 200
    assert by_short.json()["transfer_id"] == payload["transfer_id"]
    assert by_post.status_code == 200
    assert by_post.json()["transfer_id"] == payload["transfer_id"]


def test_consume_blocks_future_fetch_for_one_time_transfer() -> None:
    app = create_app()
    with TestClient(app) as client:
        create_response = client.post(
            "/transfer/create",
            json={"bundle": sample_bundle(), "ttl_seconds": 3600, "consume_once": True},
        )
        transfer_id = create_response.json()["transfer_id"]

        consume_response = client.post(f"/transfer/{transfer_id}/consume")
        fetch_after_consume = client.get(f"/transfer/{transfer_id}")

    assert consume_response.status_code == 200
    assert consume_response.json()["consumed"] is True
    assert fetch_after_consume.status_code == 410
