"""Deterministic synthetic benchmark with machine-readable provenance."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import IsolationForest

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = "1.0.0"


def dataset(rows: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    return pd.DataFrame(
        {
            "hour": rng.integers(0, 24, rows),
            "ip_freq": rng.poisson(4, rows),
            "suspicious_flag": rng.binomial(1, 0.08, rows),
        }
    )


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    index = min(len(ordered) - 1, int(np.ceil(fraction * len(ordered))) - 1)
    return ordered[index]


def run(rows: int, iterations: int, warmup: int, seed: int) -> dict[str, Any]:
    frame = dataset(rows, seed)
    model = IsolationForest(random_state=seed, contamination=0.1, n_estimators=100)
    model.fit(frame)

    for _ in range(warmup):
        model.predict(frame)

    durations = []
    result = None
    for _ in range(iterations):
        started = time.perf_counter_ns()
        result = model.predict(frame)
        durations.append((time.perf_counter_ns() - started) / 1_000_000)

    if result is None:\n        raise RuntimeError("benchmark did not execute")\n    median_ms = statistics.median(durations)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "benchmark": "isolation_forest_batch_inference",
        "parameters": {
            "rows": rows,
            "iterations": iterations,
            "warmup_iterations": warmup,
            "seed": seed,
            "n_estimators": 100,
            "contamination": 0.1,
        },
        "metrics": {
            "latency_median_ms": round(median_ms, 3),
            "latency_p95_ms": round(percentile(durations, 0.95), 3),
            "throughput_rows_per_second": round(rows / (median_ms / 1000), 2),
            "anomalies_last_iteration": int((result == -1).sum()),
        },
        "provenance": {
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "scikit_learn": sklearn.__version__,
            "dataset_sha256": hashlib.sha256(\n                frame.to_csv(index=False).encode("utf-8"), usedforsecurity=False\n            ).hexdigest(),
        },
    }
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=10_000)
    parser.add_argument("--iterations", type=int, default=20)
    parser.add_argument("--warmup", type=int, default=3)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts" / "benchmark.json")
    args = parser.parse_args()
    if min(args.rows, args.iterations) < 1 or args.warmup < 0:
        parser.error("rows and iterations must be positive; warmup must be non-negative")

    result = run(args.rows, args.iterations, args.warmup, args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
