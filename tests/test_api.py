from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_root():
    response = client.get("/")

    assert response.status_code == 200

    assert response.json() == {
        "message": "IntelliVoice AI backend is running!"
    }


def test_health():
    response = client.get("/health")

    assert response.status_code == 200

    assert response.json() == {
        "status": "healthy"
    }


def test_chat():
    with patch(
        "backend.main.generate_response",
        return_value=(
            "Artificial Intelligence enables computers "
            "to perform intelligent tasks."
        )
    ):
        response = client.post(
            "/chat",
            json={
                "message": "What is artificial intelligence?"
            }
        )

    assert response.status_code == 200

    assert response.json() == {
        "response": (
            "Artificial Intelligence enables computers "
            "to perform intelligent tasks."
        )
    }