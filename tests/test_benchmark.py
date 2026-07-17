import json
import sys

import pytest

from benchmarks.run_benchmark import main, percentile, run


def test_benchmark_is_deterministic_and_has_provenance() -> None:
    first = run(rows=100, iterations=2, warmup=0, seed=42)
    second = run(rows=100, iterations=2, warmup=0, seed=42)

    assert first["schema_version"] == "1.0.0"
    assert first["provenance"]["dataset_sha256"] == second["provenance"]["dataset_sha256"]
    first_anomalies = first["metrics"]["anomalies_last_iteration"]
    second_anomalies = second["metrics"]["anomalies_last_iteration"]
    assert first_anomalies == second_anomalies
    assert first["metrics"]["latency_median_ms"] > 0
    assert first["metrics"]["throughput_rows_per_second"] > 0
    assert first["metrics"]["latency_min_ms"] <= first["metrics"]["latency_max_ms"]


def test_benchmark_cli_writes_machine_readable_result(tmp_path, monkeypatch) -> None:
    output = tmp_path / "result.json"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "benchmark",
            "--rows",
            "20",
            "--iterations",
            "1",
            "--warmup",
            "0",
            "--output",
            str(output),
        ],
    )
    main()
    assert json.loads(output.read_text())["parameters"]["rows"] == 20


def test_benchmark_rejects_invalid_contract(monkeypatch) -> None:
    with pytest.raises(RuntimeError, match="did not execute"):
        run(rows=1, iterations=0, warmup=0, seed=1)
    monkeypatch.setattr(sys, "argv", ["benchmark", "--rows", "0"])
    with pytest.raises(SystemExit):
        main()
    assert percentile([3.0, 1.0, 2.0], 0.5) == 2.0
