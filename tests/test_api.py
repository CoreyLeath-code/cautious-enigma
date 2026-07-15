from unittest.mock import patch

from fastapi.testclient import TestClient

from app.api import app

client = TestClient(app)


def test_health_and_readiness() -> None:
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/ready").status_code == 200
    assert client.get("/live").status_code == 200


def test_metrics_are_exposed() -> None:
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "cautious_enigma_http_requests_total" in response.text


def test_prediction_contract_and_success() -> None:
    payload = {"data": {"hour": 12, "ip_freq": 2, "suspicious_flag": 1}}
    with patch("app.api.run_realtime_inference", return_value=[-1]):
        response = client.post("/predict", json=payload)
    assert response.status_code == 200
    assert response.json() == {"prediction": [-1]}


def test_prediction_rejects_unknown_fields() -> None:
    response = client.post("/predict", json={"data": {}, "unknown": True})
    assert response.status_code == 422
