"""Training-consistent real-time and batch inference orchestration."""

import logging
from pathlib import Path
from typing import Any

import pandas as pd

from src.models.inference import get_inference_engine
from src.pipelines.preprocess import get_preprocessor
from src.utils.config import get_config

logger = logging.getLogger(__name__)


class InferencePipeline:
    def __init__(self) -> None:
        self.cfg = get_config()
        self.preprocessor = get_preprocessor()
        self.engine = get_inference_engine()
        self.features = self.cfg.get("data.features")
        if not self.features:
            raise ValueError("Missing data.features in config.yaml")

    def predict(self, data: Any) -> list[Any]:
        if isinstance(data, dict):
            frame = pd.DataFrame([data])
        elif isinstance(data, list):
            frame = pd.DataFrame(data)
        elif isinstance(data, pd.DataFrame):
            frame = data.copy()
        else:
            raise ValueError("Input must be a dict, list of dicts, or DataFrame")
        return self.engine.predict(self.preprocessor.transform(frame))

    def batch_predict(
        self, input_path: str, output_path: str | None = None
    ) -> pd.DataFrame:
        source = Path(input_path)
        if not source.is_file():
            raise FileNotFoundError(f"Input dataset not found: {source}")
        if source.suffix.lower() == ".csv":
            frame = pd.read_csv(source)
        elif source.suffix.lower() in {".parquet", ".pq"}:
            frame = pd.read_parquet(source)
        else:
            raise ValueError("Only CSV and Parquet batch inputs are supported")

        result = frame.copy()
        result["prediction"] = self.engine.predict(self.preprocessor.transform(frame))
        if output_path:
            destination = Path(output_path)
            if destination.suffix == "":
                destination = destination.with_suffix(".csv")
            destination.parent.mkdir(parents=True, exist_ok=True)
            result.to_csv(destination, index=False)
        return result


def run_realtime_inference(data: Any) -> list[Any]:
    return InferencePipeline().predict(data)


def run_batch_inference(
    input_file: str, output_file: str | None = None
) -> pd.DataFrame:
    return InferencePipeline().batch_predict(input_file, output_file)
