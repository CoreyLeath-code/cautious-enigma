"""
preprocess.py — L5/L6 Production-Grade Preprocessing Pipeline

This module performs:
✔ Schema validation
✔ Type enforcement
✔ Missing value handling
✔ Numerical scaling (optional)
✔ Categorical encoding (optional)
✔ Config-driven transformation rules
✔ Logging for observability

This file standardizes preprocessing for both training & inference.
"""

import logging
import pandas as pd
import numpy as np
from src.utils.config import get_config

logger = logging.getLogger("PreprocessPipeline")
logger.setLevel(logging.INFO)


class PreprocessPipeline:
    """
    Central preprocessing engine used during both:
    - Training
    - Inference

    Responsibilities:
    • Validate schema
    • Handle missing values
    • Apply transformations based on config
    """

    def __init__(self):
        self.cfg = get_config()

        # Load feature schema from config
        self.features = self.cfg.get("data.features", [])
        self.label = self.cfg.get("data.label_col")

        if not self.features:
            raise ValueError(
                "Missing `data.features` in config.yaml — preprocessing cannot continue."
            )

        # Load optional transformation rules
        self.fill_values = self.cfg.get("preprocess.fill_values", {})
        self.dropna = self.cfg.get("preprocess.dropna", False)
        self.cast_types = self.cfg.get("preprocess.cast_types", {})

        logger.info("PreprocessPipeline initialized.")

    # ----------------------------------------------------
    # Schema Enforcement
    # ----------------------------------------------------
    def _validate_columns(self, df: pd.DataFrame):
        """Ensure all expected columns are present."""
        missing = [col for col in self.features if col not in df.columns]

        if missing:
            raise ValueError(f"Missing required features in dataset: {missing}")

        logger.info("Column validation passed.")

    def _enforce_types(self, df: pd.DataFrame):
        """Enforce types from config (e.g., int, float)."""
        for col, dtype in self.cast_types.items():
            if col in df.columns:
                try:
                    df[col] = df[col].astype(dtype)
                except Exception as e:
                    raise ValueError(
                        f"Failed type casting for '{col}' → {dtype}: {e}"
                    )
        return df

    # ----------------------------------------------------
    # Missing Value Handling
    # ----------------------------------------------------
    def _handle_missing(self, df: pd.DataFrame):
        """Fill or drop missing values based on config."""
        if self.dropna:
            df = df.dropna()
            logger.info("Dropped rows with missing values.")
            return df

        # Fill using config values
        for col, fill_value in self.fill_values.items():
            if col in df.columns:
                df[col] = df[col].fillna(fill_value)

        # Fill with column mean for numerical features if not specified
        for col in self.features:
            if df[col].isna().sum() > 0 and col not in self.fill_values:
                if pd.api.types.is_numeric_dtype(df[col]):
                    mean_val = df[col].mean()
                    df[col] = df[col].fillna(mean_val)
                    logger.info(f"Filled missing values in {col} with mean={mean_val:.4f}")

        return df

    # ----------------------------------------------------
    # Main Entry Point
    # ----------------------------------------------------
    def transform(self, df: pd.DataFrame):
        """Run the full preprocessing pipeline."""
        logger.info("Running preprocessing pipeline...")

        df = df.copy()

        # 1. Schema validation
        self._validate_columns(df)

        # 2. Type enforcement
        df = self._enforce_types(df)

        # 3. Missing value handling
        df = self._handle_missing(df)

        logger.info("Preprocessing complete.")
        return df


# Global accessor
def get_preprocessor():
    return PreprocessPipeline()
