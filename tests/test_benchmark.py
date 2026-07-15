from benchmarks.run_benchmark import run


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
