import json

import pytest

from src.utils.model_registry import ModelRegistry


def registry(tmp_path, monkeypatch) -> ModelRegistry:
    monkeypatch.setenv("MODEL_REGISTRY_DIR", str(tmp_path))
    return ModelRegistry()


def test_registry_versions_and_verifies_artifacts(tmp_path, monkeypatch) -> None:
    store = registry(tmp_path, monkeypatch)
    first = store.save_model({"coefficient": 1}, "detector")
    second = store.save_model({"coefficient": 2}, "detector")
    assert first["version"] == 1
    assert second["version"] == 2
    assert store.load_model("detector") == {"coefficient": 2}
    assert store.load_model("detector", 1) == {"coefficient": 1}


def test_registry_rejects_paths_versions_and_missing_models(tmp_path, monkeypatch) -> None:
    store = registry(tmp_path, monkeypatch)
    with pytest.raises(ValueError, match="safe identifier"):
        store.save_model({}, "../escape")
    with pytest.raises(ValueError, match="positive integer"):
        store.load_model("detector", 0)
    with pytest.raises(FileNotFoundError):
        store.load_model("detector", 1)


def test_registry_detects_model_and_metadata_tampering(tmp_path, monkeypatch) -> None:
    store = registry(tmp_path, monkeypatch)
    store.save_model({"trusted": True}, "detector")
    model = tmp_path / "detector_v1.pkl"
    model.write_bytes(model.read_bytes() + b"tampered")
    with pytest.raises(RuntimeError, match="integrity"):
        store.load_model("detector", 1)

    metadata = tmp_path / "detector_v1.json"
    payload = json.loads(metadata.read_text())
    payload["fingerprint_sha256"] = 123
    metadata.write_text(json.dumps(payload))
    with pytest.raises(RuntimeError, match="integrity"):
        store.load_model("detector", 1)
