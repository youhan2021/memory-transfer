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
            },
            {
                "id": "mem_2",
                "type": "workflow",
                "title": "Review flow",
                "content": "Preview first, then import.",
                "tags": ["workflow"],
                "transferable": True,
                "sensitivity": "low",
            },
        ],
    }


def create_transfer(client: TestClient) -> dict:
    response = client.post(
        "/transfer/create",
        json={"bundle": sample_bundle(), "ttl_seconds": 600},
    )
    assert response.status_code == 200
    return response.json()


def test_lookup_returns_preview_only() -> None:
    app = create_app()
    with TestClient(app) as client:
        created = create_transfer(client)
        response = client.post("/transfer/lookup", json={"short_code": created["short_code"]})

    assert response.status_code == 200
    payload = response.json()
    assert payload["short_code"] == created["short_code"]
    assert payload["preview"]["source_agent"] == "unit-test-source"
    assert payload["preview"]["memory_count"] == 2
    assert payload["preview"]["memory_type_counts"] == {
        "project_context": 1,
        "workflow": 1,
    }
    assert payload["preview"]["requires_confirm_phrase"] is True
    assert "content" not in str(payload)


def test_fetch_compat_alias_returns_preview_only() -> None:
    app = create_app()
    with TestClient(app) as client:
        created = create_transfer(client)
        response = client.post("/transfer/fetch", json={"code": created["short_code"]})

    assert response.status_code == 200
    payload = response.json()
    assert payload["short_code"] == created["short_code"]
    assert payload["preview"]["requires_confirm_phrase"] is True
    assert "content" not in str(payload)


def test_confirm_import_succeeds_with_correct_phrase() -> None:
    app = create_app()
    with TestClient(app) as client:
        created = create_transfer(client)
        response = client.post(
            "/transfer/confirm-import",
            json={
                "short_code": created["short_code"],
                "confirm_phrase": created["confirm_phrase"],
                "import_mode": "upsert",
            },
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "consumed"
    assert payload["import_mode"] == "upsert"
    assert payload["bundle"]["memories"][0]["content"] == "One-command install is required."


def test_confirm_import_fails_with_wrong_phrase() -> None:
    app = create_app()
    with TestClient(app) as client:
        created = create_transfer(client)
        response = client.post(
            "/transfer/confirm-import",
            json={
                "short_code": created["short_code"],
                "confirm_phrase": "wrong phrase",
                "import_mode": "upsert",
            },
        )

    assert response.status_code == 403


def test_expired_transfer_cannot_be_imported() -> None:
    app = create_app()
    with TestClient(app) as client:
        created = client.post(
            "/transfer/create",
            json={"bundle": sample_bundle(), "ttl_seconds": 60},
        ).json()
        client.app.state.bundle_store._records[created["transfer_id"]].expires_at = (  # noqa: SLF001
            client.app.state.bundle_store._records[created["transfer_id"]].created_at  # noqa: SLF001
        )
        response = client.post(
            "/transfer/confirm-import",
            json={
                "short_code": created["short_code"],
                "confirm_phrase": created["confirm_phrase"],
                "import_mode": "upsert",
            },
        )

    assert response.status_code == 410


def test_consumed_transfer_cannot_be_imported_twice() -> None:
    app = create_app()
    with TestClient(app) as client:
        created = create_transfer(client)
        first = client.post(
            "/transfer/confirm-import",
            json={
                "short_code": created["short_code"],
                "confirm_phrase": created["confirm_phrase"],
                "import_mode": "upsert",
            },
        )
        second = client.post(
            "/transfer/confirm-import",
            json={
                "short_code": created["short_code"],
                "confirm_phrase": created["confirm_phrase"],
                "import_mode": "append",
            },
        )

    assert first.status_code == 200
    assert second.status_code == 410
