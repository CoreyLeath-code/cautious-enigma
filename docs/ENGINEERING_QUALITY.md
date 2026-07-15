# Engineering quality and deployment hygiene

This repository uses evidence-producing controls rather than a maturity label. A change is
promotion-ready only when all required checks pass.

## Nine deployment tiers

1. **Source integrity** — protected review path, CODEOWNERS, and least-privilege workflows.
2. **Build reproducibility** — Python 3.11 plus exact runtime and test dependency pins.
3. **Automated verification** — lint, security analysis, unit/API tests, and branch coverage.
4. **Artifact integrity** — non-root image build, vulnerability scan, and SPDX SBOM.
5. **Configuration safety** — environment injection; no committed operational credentials.
6. **Runtime hardening** — read-only root filesystem, dropped capabilities, seccomp, no token.
7. **Health and observability** — startup/liveness/readiness probes and Prometheus metrics.
8. **Safe promotion** — immutable version tags, rolling update, limits, and default-deny network.
9. **Release assurance** — semantic tag publication and keyless Cosign signatures.

## Release and rollback

1. Merge only after CI and Supply Chain checks pass.
2. Create a semantic tag such as `v1.1.0`; CI publishes and signs the matching image.
3. Verify the signature with Cosign and deploy the immutable version or digest to staging.
4. Validate health, error rate, and latency before production promotion.
5. Roll back with `kubectl rollout undo deployment/cautious-enigma` or redeploy the prior digest.
6. Record the incident, affected digest, metrics, and corrective action.

Any emergency exception must identify an owner, reason, expiry (maximum seven days), compensating
control, and follow-up issue. Exceptions never permit committed secrets or privileged containers.

## Evidence

- CI artifact `benchmark-and-coverage`: benchmark JSON and Cobertura-compatible coverage XML.
- Supply Chain artifact `sbom-spdx`: SPDX JSON inventory for the scanned image.
- GitHub Actions logs: dependency audit, Trivy findings, Kubernetes schema validation, container
  UID, and HTTP smoke probe.
