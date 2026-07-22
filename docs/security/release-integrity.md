# Release Integrity

The security and build jobs call `Akanom/python-package-governance` at immutable
commit `863aef9dd96c3ea40806d4fa0b6e78b50323ad6b`; dependency updates must review
and deliberately advance that SHA.

Every release must pass supported-Python and minimum-dependency tests,
dependency consistency and advisory audits, strict Twine validation,
distribution inspection, wheel-only installation, and separate sdist
installation. CI stores the artifact inventory and CycloneDX SBOM.

The protected publication job consumes the exact artifacts produced by the
unprivileged build job, creates a provenance attestation, and publishes through
PyPI Trusted Publishing. After publication, compare PyPI hashes with the build
inventory, install the downloaded wheel with `--only-binary=:all:`, and run a
smoke export.
