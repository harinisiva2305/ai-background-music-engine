
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_endpoint():
    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_create_music_job():
    response = client.post(
        "/api/v1/music/jobs",
        json={
            "prompt": "Calm instrumental background music",
            "duration_s": 10,
        },
    )

    assert response.status_code == 202

    data = response.json()
    assert "job_id" in data
    assert data["status"] == "queued"
    assert data["duration_s"] == 10


def test_invalid_duration_is_rejected():
    response = client.post(
        "/api/v1/music/jobs",
        json={
            "prompt": "Calm music",
            "duration_s": 301,
        },
    )

    assert response.status_code == 422


def test_missing_job_returns_404():
    response = client.get(
        "/api/v1/jobs/does-not-exist"
    )

    assert response.status_code == 404
