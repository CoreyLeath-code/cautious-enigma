# Cautious Enigma

[![CI](https://github.com/CoreyLeath-code/cautious-enigma/actions/workflows/ci.yml/badge.svg?branch=agent%2Fproduction-hardening)](https://github.com/CoreyLeath-code/cautious-enigma/actions/workflows/ci.yml?query=branch%3Aagent%2Fproduction-hardening)
[![Supply Chain](https://github.com/CoreyLeath-code/cautious-enigma/actions/workflows/supply-chain.yml/badge.svg?branch=agent%2Fproduction-hardening)](https://github.com/CoreyLeath-code/cautious-enigma/actions/workflows/supply-chain.yml?query=branch%3Aagent%2Fproduction-hardening)
![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.139-009688?logo=fastapi&logoColor=white)
![Coverage gate](https://img.shields.io/badge/coverage%20gate-%E2%89%A590%25-success)
![Dependency audit](https://img.shields.io/badge/pip--audit-0%20known%20CVEs-success)
![Deployment hygiene](https://img.shields.io/badge/deployment%20hygiene-9%2F9-success)
![Container](https://img.shields.io/badge/container-non--root%20%7C%20read--only-2496ED?logo=docker&logoColor=white)
![SBOM](https://img.shields.io/badge/SBOM-SPDX-4c1)
![Reproducible](https://img.shields.io/badge/benchmark-seeded%20%2B%20versioned-blueviolet)
[![Benchmark](https://img.shields.io/badge/reference%20p99-4.824%20ms-blueviolet)](#reference-benchmark-results)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

Cautious Enigma is a reproducible anomaly-detection pipeline and observable FastAPI service.
It converts security log events into time, source-frequency, and keyword features, then applies
an Isolation Forest detector. The repository is intentionally explicit about what is measured:
systems benchmarks do not establish predictive model quality.


## Production Readiness Guide

> This section is the portfolio audit entry point for **cautious-enigma**. It describes an engineering promotion path; it is not a claim that the repository is already production-authorized.

[![CI](https://img.shields.io/github/actions/workflow/status/CoreyLeath-code/cautious-enigma/ci.yml?branch=main&label=CI)](https://github.com/CoreyLeath-code/cautious-enigma/actions) [![License](https://img.shields.io/github/license/CoreyLeath-code/cautious-enigma)](https://github.com/CoreyLeath-code/cautious-enigma/blob/main/LICENSE)

### Architecture flowchart

```mermaid
flowchart LR
    Client --> Gateway --> Services[API + workers] --> Events[(Event bus)] --> Store[(State)]
```

### Quickstart and local validation

The supported local path should be reproducible from a clean checkout. The inferred stack for this repository is **Python/platform services**.

```bash
python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
pytest -q
```

If the project uses external services, model artifacts, cloud credentials, or private data, start them through documented local fixtures or mocks. Never place secrets or identifiable records in the repository.

### Research-style metrics and benchmarks

| Evidence | Required record |
|---|---|
| Correctness | Test command, commit SHA, runtime, and pass/fail result |
| Performance | Warm-up, sample count, concurrency, median, p95, p99, throughput, and memory |
| Data/model quality | Dataset version, split strategy, leakage controls, calibration, subgroup results, and uncertainty |
| Runtime | Image digest, health-check latency, resource limits, and rollback target |
| Security | Dependency, secret, SAST, container, and SBOM results |

A benchmark number belongs in a versioned artifact tied to a commit and hardware/runtime description. Engineering benchmarks must not be presented as clinical, financial, safety, or model-quality validation without the appropriate domain evidence.

### Extended Q&A

**What is production-ready for this repository?**  
A reproducible build, tested public contract, controlled configuration, observable runtime, documented security boundary, versioned artifacts, and a tested rollback path.

**What must remain explicit?**  
The intended use, excluded use, data/credential handling, model or algorithm limitations, and which metrics are measured versus aspirational.

**What should be completed next?**  
Use the linked production-readiness issue for this repository as the checklist. Resolve missing tests, deployment instructions, observability, supply-chain controls, and release evidence before attaching a production claim.


## Research question

**Can a fixed Isolation Forest configuration produce deterministic anomaly decisions while
providing auditable batch-inference latency and throughput measurements?**

The benchmark uses a seeded synthetic feature generator and records the dataset SHA-256,
parameters, dependency versions, platform, UTC generation time, latency distribution, throughput,
and anomaly count in a versioned JSON document.

## Verifiable metrics

| Evidence | Metric or invariant | Acceptance rule | Verification |
|---|---|---:|---|
| Unit/API suite | Branch coverage | >= 90% | `pytest`; inspect `coverage.xml` |
| Static analysis | Ruff and Bandit findings | 0 blocking findings | `make quality` |
| Dependencies | Known vulnerable runtime packages | 0 audit failures | `pip-audit -r Requirements.txt` |
| Container | Runtime UID | exactly `10001` | CI executes `id -u` inside the image |
| Runtime | Health probe | HTTP 200 within 40 s | CI container smoke test |
| Kubernetes | Schema errors | 0 in strict mode | Kubeconform CI step |
| Supply chain | HIGH/CRITICAL actionable findings | 0 | Trivy repository and image scans |
| Benchmark | Median/p95 latency and rows/s | measured, not gated | CI `benchmark.json` artifact |
| Reproducibility | Dataset hash and anomaly count | identical for same seed/config | `tests/test_benchmark.py` |

The latest numerical performance measurements are attached to each successful CI run as
`benchmark-and-coverage/artifacts/benchmark.json`. This avoids presenting a stale result as a
universal claim. GitHub records the runner image and commit alongside the artifact.

## Reference benchmark results

| Metric | Result | Interpretation |
|---|---:|---|
| Median batch latency | 4.620 ms | Central latency across five timed iterations |
| Mean batch latency | 4.671 ms | Arithmetic mean across timed iterations |
| P95 / P99 latency | 4.824 / 4.824 ms | Observed tail latency in this small reference sample |
| Min / max latency | 4.601 / 4.824 ms | Observed range |
| Throughput | 216,440.85 rows/s | 1,000 rows divided by median latency |
| Detected anomalies | 99 / 1,000 | Deterministic output for the configured synthetic dataset |

**Reference environment.** Windows 11, Python 3.12.13, NumPy 1.26.4, pandas 2.2.3,
scikit-learn 1.5.2; generated 2026-07-17. The protocol used seed 42, 100 estimators,
contamination 0.1, one warm-up, and five timed iterations. Dataset SHA-256:
`4f3218f02149d84c2c58c156f7d1938da03e03c8d9c1f7a9a5680c443f0e5fcc`.

This is descriptive systems evidence from one machine, not a confidence interval, production SLO,
or model-quality result. The five-iteration sample is intentionally lightweight for reproducibility;
use the CI artifact and a larger pre-registered run before making comparative performance claims.

## Benchmark protocol

The CI protocol is 1,000 rows, one warm-up, five timed iterations, seed 42, 100 trees, and
contamination 0.1. Local research runs default to 10,000 rows, three warm-ups, and 20 timed
iterations.

```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python benchmarks/run_benchmark.py --output artifacts/benchmark.json
pytest
```

A valid result contains:

- `schema_version` and the complete benchmark parameter set;
- median and p95 batch latency in milliseconds;
- median-derived rows per second and last-iteration anomaly count;
- Python, NumPy, pandas, scikit-learn, OS/platform, UTC time, and dataset SHA-256.

Latency is expected to vary by CPU load, runner generation, operating system, and power policy.
Compare performance only when the parameter block and environment metadata are compatible.
The synthetic benchmark tests computational behavior, not real-world recall, fairness, drift,
or threat-detection efficacy. Predictive accuracy requires a versioned, labeled evaluation set
that this repository does not currently include.

## API

```bash
uvicorn app.api:app --host 127.0.0.1 --port 8000
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/metrics
curl -X POST http://127.0.0.1:8000/predict \
  -H "x-api-key: $CAUTIOUS_API_KEY" \
  -H "content-type: application/json" \
  -d '{"data":{"hour":12,"ip_freq":3,"suspicious_flag":1}}'
```

Set `CAUTIOUS_API_KEY` in production; prediction routes then require the `x-api-key` header.
`/batch_predict` accepts at most 1,000 inline records and never accepts server filesystem paths.
The prediction endpoint requires a trained `baseline_classifier` in the model registry. Registry
artifacts are SHA-256 verified before deserialization. Missing models return a sanitized HTTP 503;
invalid features return HTTP 422. Prometheus telemetry exposes bounded-cardinality request counts
and latency histograms at `/metrics`.

## Architecture

```mermaid
flowchart LR
    A[Log events] --> B[Preprocess]
    B --> C[Feature extraction]
    C --> D[Isolation Forest]
    D --> E[Threat indices]
    D --> F[FastAPI]
    F --> G[Health and metrics]
    H[Seeded synthetic data] --> I[Benchmark runner]
    I --> J[Versioned JSON evidence]
```

| Path | Responsibility |
|---|---|
| `data_loader.py`, `feature_engineering.py` | Baseline log-to-feature pipeline |
| `model.py`, `detector.py` | Deterministic training and anomaly decisions |
| `app/` | Validated API, probes, and Prometheus telemetry |
| `src/` | Configurable training and inference components |
| `benchmarks/` | Reproducible research benchmark |
| `tests/` | Behavior, API contract, and provenance verification |
| `.github/workflows/` | Quality, benchmark, deployment, and supply-chain evidence |

Operational decisions, residual risks, and production readiness are recorded in
[the audit](docs/AUDIT.md), [deployment runbook](docs/DEPLOYMENT.md), and
[production checklist](docs/PRODUCTION_CHECKLIST.md).

## Deployment hygiene

Nine promotion controls cover source integrity, repeatable builds, automated verification,
artifact integrity, configuration safety, runtime hardening, observability, safe promotion, and
signed releases. The detailed control/evidence matrix, rollback procedure, and time-bounded
exception policy are in [docs/ENGINEERING_QUALITY.md](docs/ENGINEERING_QUALITY.md).

```bash
docker compose up --build
docker build -t cautious-enigma:local .
kubectl apply -f network-policy.yaml -f deployment.yaml -f service.yaml
```

The Kubernetes example uses a non-root read-only container, dropped capabilities, RuntimeDefault
seccomp, disabled service-account token mounting, resource bounds, three probe types, a rolling
strategy, an immutable version tag, and default-deny networking. Supply Chain CI scans source and
image, emits an SPDX SBOM, publishes semantic-tag images to GHCR, and signs them keylessly.

## Responsible use

Isolation Forest outputs are review signals, not proof of malicious activity. Keep a human in the
decision loop, protect log data, monitor false positives and drift, and validate against a
representative labeled dataset before operational enforcement.

## License

MIT. See [LICENSE](LICENSE).
