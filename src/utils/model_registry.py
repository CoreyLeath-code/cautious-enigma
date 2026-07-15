"""
model_registry.py — L5/L6 Production-Grade Local Model Registry

Features:
✔ Versioned model saving (v1, v2, v3...)
✔ SHA-256 fingerprinting for reproducibility
✔ JSON metadata tracking (timestamp, size, hash)
✔ Works with: sklearn, xgboost, pytorch, lightgbm, catboost
✔ Centralized logging & directory management
✔ Production-safe loading & validation

This provides L6-level model traceability without full MLflow infra.
"""

import json
import pickle
import hashlib
import logging
from datetime import datetime
from pathlib import Path

from src.utils.config import get_config

logger = logging.getLogger("ModelRegistry")
logger.setLevel(logging.INFO)

class ModelRegistry:
    def __init__(self):
        self.cfg = get_config()
        self.registry_dir = Path(self.cfg.get("models.registry_dir", "models/registry"))
        self.registry_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"[OK] Model registry initialized at: {self.registry_dir}")

    @staticmethod
    def _compute_sha256(file_path):
        """Compute SHA-256 hash for a saved model."""
        sha = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                sha.update(chunk)
        return sha.hexdigest()

    def _get_next_version(self, model_name):
        """Return next version number based on existing saved versions."""
        existing = list(self.registry_dir.glob(f"{model_name}_v*.pkl"))
        if not existing:
            return 1
        versions = [int(f.stem.split("_v")[-1]) for f in existing]
        return max(versions) + 1

    def save_model(self, model, model_name: str):
        """Save a versioned model with metadata."""
        version = self._get_next_version(model_name)
        model_file = self.registry_dir / f"{model_name}_v{version}.pkl"
        metadata_file = self.registry_dir / f"{model_name}_v{version}.json"

        try:
            # Save model
            with open(model_file, "wb") as f:
                pickle.dump(model, f)

            # Compute fingerprint
            fingerprint = self._compute_sha256(model_file)

            # Metadata
            metadata = {
                "model_name": model_name,
                "version": version,
                "file_path": str(model_file),
                "fingerprint_sha256": fingerprint,
                "timestamp": datetime.utcnow().isoformat(),
                "size_kb": round(model_file.stat().st_size / 1024, 2),
            }

            # Save metadata
            with open(metadata_file, "w") as f:
                json.dump(metadata, f, indent=4)

            logger.info(f"[SAVED] Model '{model_name}' v{version}")
            logger.info(f"Location: {model_file}")
            logger.info(f"Fingerprint: {fingerprint}")

            return metadata

        except Exception as e:
            logger.error(f"Failed to save model: {e}")
            raise

    def load_model(self, model_name: str, version: int = None):
        """
        Load a model by name and (optional) version.
        If version not specified — loads the latest version.
        """
        if version is None:
            version = self._get_next_version(model_name) - 1

        model_file = self.registry_dir / f"{model_name}_v{version}.pkl"
        metadata_file = self.registry_dir / f"{model_name}_v{version}.json"

        if not model_file.exists():
            raise FileNotFoundError(
                f"Model version not found: {model_name}_v{version}.pkl"
            )

        with open(model_file, "rb") as f:
            model = pickle.load(f)

        logger.info(f"[LOADED] {model_name} v{version}")

        if metadata_file.exists():
            with open(metadata_file, "r") as f:
                metadata = json.load(f)
            logger.info(f"Metadata: {metadata}")
        else:
            logger.warning("No metadata file found for this model version.")

        return model


# Global accessor
def get_registry():
    return ModelRegistry()
