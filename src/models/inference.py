"""
inference.py — L5/L6 Production-Grade Inference Engine

This module powers real-time or batch predictions.
✔ Loads latest version of model from registry
✔ Enforces correct feature ordering
✔ Cleans & validates incoming requests
✔ Compatible with FastAPI, Flask, and AWS Lambda
✔ Logs all inference steps
"""

import logging
import numpy as np
import pandas as pd
from src.utils.config import get_config
from src.utils.model_registry import get_registry

logger = logging.getLogger("InferenceEngine")
logger.setLevel(logging.INFO)


class InferenceEngine:
    """
    Central production inference engine.
    
    Responsibilities:
    - Load latest model from registry
    - Validate input data
    - Enforce column ordering from config
    - Run predictions safely
    """

    def __init__(self):
        logger.info("Initializing InferenceEngine...")

        self.cfg = get_config()
        self.registry = get_registry()

        # Load expected schema
        self.label_col = self.cfg.get("data.label_col")
        self.expected_features = self.cfg.get("data.features")

        if not self.expected_features:
            raise ValueError(
                "Missing `data.features` in config.yaml — needed for feature ordering."
            )

        # Load latest model
        logger.info("Loading latest model from registry...")
        self.model = self.registry.load_model("baseline_classifier")

    def _validate_and_format_input(self, data):
        """
        Accepts:
        - dict
        - dict list
        - pandas DataFrame

        Converts everything into a properly ordered DataFrame.
        """

        if isinstance(data, dict):
            # Single record → convert to DataFrame
            df = pd.DataFrame([data])

        elif isinstance(data, list):
            # List of dicts
            df = pd.DataFrame(data)

        elif isinstance(data, pd.DataFrame):
            df = data.copy()

        else:
            raise ValueError(
                "InferenceEngine only accepts dict, list[dict], or DataFrame."
            )

        # Ensure required columns present
        missing = [
            col for col in self.expected_features if col not in df.columns
        ]
        if missing:
            raise ValueError(f"Missing required features: {missing}")

        # Order columns correctly
        df = df[self.expected_features]

        logger.info(f"Validated input — shape: {df.shape}")
        return df

    def predict(self, data):
        """
        Run prediction with validated and ordered data.
        Returns raw model outputs.
        """
        try:
            df = self._validate_and_format_input(data)
            preds = self.model.predict(df)

            logger.info(f"Predictions generated — count: {len(preds)}")
            return preds.tolist()

        except Exception as e:
            logger.error(f"[INFERENCE ERROR] {e}")
            raise


# Global accessor for APIs
def get_inference_engine():
    return InferenceEngine()
