from fastapi.testclient import TestClient

from memory_transfer_server.main import create_app


def test_health_endpoint() -> None:
    app = create_app()
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["service"] == "memory-transfer-server"
