# Production audit

## Executive summary

The service has a credible CI, container, Kubernetes, observability, and supply-chain foundation.
This hardening pass closed the highest-risk runtime boundary: batch prediction previously accepted
arbitrary server input and output paths. Batch requests now contain bounded inline records, and
prediction routes support constant-time API-key authentication.

## Findings and disposition

| Severity | Finding | Disposition |
|---|---|---|
| Critical | HTTP clients could direct batch inference to read and write server paths | Fixed: filesystem parameters removed; schema permits 1-1,000 inline records only |
| High | Prediction routes had no authentication control | Fixed: optional `CAUTIOUS_API_KEY`; Kubernetes reads it from a Secret |
| High | Pickled model artifacts were deserialized without integrity verification | Fixed: metadata SHA-256 is mandatory and checked before load |
| Medium | Test gate excluded production modules and required only 55% coverage | Fixed: critical modules included; 90% threshold; measured 97.65% locally |
| Medium | Committed environment file encouraged unsafe secret handling | Fixed: removed; `.env.example` documents non-secret configuration |
| Medium | Package metadata contained invalid executable shell text | Fixed: removed duplicate `setup.py`; setuptools uses `pyproject.toml` |
| Low | Benchmark omitted tail and range statistics | Fixed: min, mean, p99, and max added |

## Verification evidence

- 15 tests passed; 97.65% statement/branch coverage across critical API, benchmark, and registry code.
- Ruff and Bandit completed with zero findings.
- `pip-audit -r Requirements.txt` found no known vulnerabilities on 2026-07-17.
- Reproducible 1,000-row local benchmark: median 4.620 ms, p95/p99 4.824 ms, 216,440.85 rows/s.

These measurements characterize one Windows/Python 3.12 environment and are not an SLO or a claim
of model accuracy. CI artifacts remain the authoritative per-commit evidence.

## Residual risks

- Pickle remains unsafe if an attacker can modify both an artifact and its metadata. The registry
  must be mounted read-only from trusted storage; migrate to a non-executable model format when feasible.
- Authentication is a shared-key control. Internet-facing deployments should terminate TLS and use
  workload identity or an API gateway for rotation, authorization, rate limiting, and audit trails.
- Predictive efficacy is not established without a versioned, representative labeled dataset.
