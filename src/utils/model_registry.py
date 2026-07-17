"""Versioned local model registry with artifact integrity verification."""

from __future__ import annotations

import hashlib
import json
import logging
import os
import pickle  # nosec B403
import re
import secrets
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from src.utils.config import get_config

logger = logging.getLogger(__name__)


class ModelRegistry:
    """Persist trusted local artifacts; never load models from attacker-writable storage."""

    MODEL_NAME = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{0,63}$")

    def __init__(self) -> None:
        configured = os.getenv(
            "MODEL_REGISTRY_DIR",
            get_config().get("models.registry_dir", "models/registry"),
        )
        self.registry_dir = Path(configured).resolve()
        self.registry_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def _validate_name(cls, model_name: str) -> None:
        if not cls.MODEL_NAME.fullmatch(model_name):
            raise ValueError("model_name must be a safe identifier")

    @staticmethod
    def _compute_sha256(file_path: Path) -> str:
        digest = hashlib.sha256()
        with file_path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(64 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def _get_next_version(self, model_name: str) -> int:
        self._validate_name(model_name)
        versions = [
            int(path.stem.rsplit("_v", 1)[1])
            for path in self.registry_dir.glob(f"{model_name}_v*.pkl")
            if path.stem.rsplit("_v", 1)[1].isdigit()
        ]
        return max(versions, default=0) + 1

    def save_model(self, model: Any, model_name: str) -> dict[str, Any]:
        self._validate_name(model_name)
        version = self._get_next_version(model_name)
        model_file = self.registry_dir / f"{model_name}_v{version}.pkl"
        metadata_file = model_file.with_suffix(".json")
        with model_file.open("wb") as handle:
            pickle.dump(model, handle)
        fingerprint = self._compute_sha256(model_file)
        metadata = {
            "model_name": model_name,
            "version": version,
            "file_name": model_file.name,
            "fingerprint_sha256": fingerprint,
            "created_at_utc": datetime.now(UTC).isoformat(),
            "size_bytes": model_file.stat().st_size,
        }
        metadata_file.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
        logger.info("Registered %s v%s (%s)", model_name, version, fingerprint)
        return metadata

    def load_model(self, model_name: str, version: int | None = None) -> Any:
        self._validate_name(model_name)
        selected = self._get_next_version(model_name) - 1 if version is None else version
        if not isinstance(selected, int) or selected < 1:
            raise ValueError("version must be a positive integer")
        model_file = self.registry_dir / f"{model_name}_v{selected}.pkl"
        metadata_file = model_file.with_suffix(".json")
        if not model_file.is_file() or not metadata_file.is_file():
            raise FileNotFoundError(f"Model or metadata not found: {model_name}_v{selected}")
        metadata = json.loads(metadata_file.read_text(encoding="utf-8"))
        expected = metadata.get("fingerprint_sha256")
        actual = self._compute_sha256(model_file)
        if not isinstance(expected, str) or not secrets.compare_digest(expected, actual):
            raise RuntimeError("model artifact integrity check failed")
        # Pickle can execute code. Integrity and trusted registry ownership are mandatory controls.
        with model_file.open("rb") as handle:
            model = pickle.load(handle)  # noqa: S301  # nosec B301
        logger.info("Loaded %s v%s (%s)", model_name, selected, actual)
        return model


def get_registry() -> ModelRegistry:
    return ModelRegistry()
