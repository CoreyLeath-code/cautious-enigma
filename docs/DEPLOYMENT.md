# Deployment and rollback runbook

## Preconditions

1. Require successful CI and supply-chain workflows for the exact commit.
2. Review the generated SBOM and confirm zero actionable HIGH/CRITICAL findings.
3. Create Kubernetes Secret `cautious-enigma-api` with key `api-key`; never commit its value.
4. Pin the promoted image by digest and ensure the model registry is trusted and read-only.

## Deploy

Apply `configmap.yaml`, `network-policy.yaml`, `deployment.yaml`, and `service.yaml`. Confirm rollout,
then verify `/health`, `/ready`, and `/metrics`. Send an authenticated canary prediction and confirm
expected status, latency, logs, and bounded metric labels before increasing traffic.

## Rollback

Stop promotion on elevated error rate, latency regression, readiness failure, or unexpected model
behavior. Roll back to the previously recorded image digest, verify probes and a canary request, and
preserve the failed pod logs, image digest, configuration revision, and model version for analysis.
Rotate the API key immediately if exposure is suspected.
