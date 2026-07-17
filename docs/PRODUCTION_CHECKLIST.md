# Production readiness checklist

- [ ] CI, security scan, dependency audit, benchmark, and container smoke test pass for the commit.
- [ ] Image digest, SBOM, signature, configuration revision, and model version are recorded.
- [ ] API key is sourced from a secret manager and rotation ownership is assigned.
- [ ] TLS, gateway rate limits, request-size limits, and network policy are enforced.
- [ ] Model registry is trusted, read-only, backed up, and artifacts pass integrity verification.
- [ ] Dashboards cover availability, request rate, errors, latency, saturation, and model failures.
- [ ] Alerts have owners, actionable thresholds, and links to this runbook.
- [ ] Capacity and failure-mode tests meet the service's documented SLOs.
- [ ] Rollback to the previous image digest and model version has been rehearsed.
- [ ] Privacy, retention, access logging, and incident-response requirements have owner approval.
