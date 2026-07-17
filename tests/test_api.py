from unittest.mock import patch

from fastapi.testclient import TestClient

from app.api import app

client = TestClient(app)


def test_public_operational_endpoints() -> None:
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/ready").json() == {"ready": True}
    assert client.get("/live").status_code == 200
    assert client.get("/").json()["service"] == "cautious-enigma"
    assert "cautious_enigma_http_requests_total" in client.get("/metrics").text


def test_prediction_contract_and_success() -> None:
    payload = {"data": {"hour": 12, "ip_freq": 2, "suspicious_flag": 1}}
    with patch("app.api.run_realtime_inference", return_value=[-1]):
        response = client.post("/predict", json=payload)
    assert response.status_code == 200
    assert response.json() == {"prediction": [-1]}


def test_prediction_authentication_when_configured(monkeypatch) -> None:
    monkeypatch.setenv("CAUTIOUS_API_KEY", "expected-secret")
    payload = {"data": {"hour": 12}}
    assert client.post("/predict", json=payload).status_code == 401
    assert client.post("/predict", json=payload, headers={"X-API-Key": "wrong"}).status_code == 401
    with patch("app.api.run_realtime_inference", return_value=[1]):
        response = client.post(
            "/predict", json=payload, headers={"X-API-Key": "expected-secret"}
        )
    assert response.status_code == 200


def test_prediction_maps_input_and_model_failures() -> None:
    with patch("app.api.run_realtime_inference", side_effect=ValueError("missing feature")):
        response = client.post("/predict", json={"data": {"hour": 1}})
    assert response.status_code == 422
    with patch("app.api.run_realtime_inference", side_effect=RuntimeError("load failed")):
        response = client.post("/predict", json={"data": {"hour": 1}})
    assert response.status_code == 503
    assert response.json()["detail"] == "Model unavailable"


def test_batch_is_inline_bounded_and_never_accepts_file_paths() -> None:
    records = [{"hour": 1.0}, {"hour": 2.0}]
    with patch("app.api.run_realtime_inference", return_value=[1, -1]) as inference:
        response = client.post("/batch_predict", json={"records": records})
    assert response.json() == {
        "status": "success",
        "rows_processed": 2,
        "predictions": [1, -1],
    }
    inference.assert_called_once_with(records)
    assert client.post("/batch_predict", json={"input_file": "/etc/passwd"}).status_code == 422


def test_batch_rejects_failures_and_unknown_fields() -> None:
    with patch("app.api.run_realtime_inference", side_effect=FileNotFoundError("model")):
        assert client.post("/batch_predict", json={"records": [{"hour": 1}]}).status_code == 422
    with patch("app.api.run_realtime_inference", side_effect=RuntimeError("model")):
        assert client.post("/batch_predict", json={"records": [{"hour": 1}]}).status_code == 503
    assert client.post("/predict", json={"data": {}, "unknown": True}).status_code == 422
