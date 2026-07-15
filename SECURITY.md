# Security policy

## Supported versions

Security fixes are applied to the default branch and the latest tagged release.

## Reporting

Do not disclose vulnerabilities in a public issue. Use GitHub's private vulnerability
reporting for this repository. Include the affected commit, reproduction steps, impact,
and a minimal proof of concept. Maintainers will acknowledge reports within five business
days.

Secrets must come from the deployment platform. Example manifests contain no credentials.
Images are scanned in CI, release images receive an SPDX SBOM, and tagged images are signed
keylessly with Cosign.
