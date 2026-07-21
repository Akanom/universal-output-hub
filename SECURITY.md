# Security Policy

## Supported versions

Security fixes are provided for the latest released minor version and current
development branch on Python 3.10–3.12.

## Reporting a vulnerability

Use GitHub's private security-advisory form. Do not publish exploit details,
credentials, private data, or unpublished research material in a public issue.
Include the affected version or commit, impact, reproduction steps, and any
suggested mitigation.

The maintainer aims to acknowledge reports within five business days and give
an initial status update within ten business days. Coordinated disclosure is
preferred.

## Dependency and release policy

Confirmed critical and high vulnerabilities block release unless an owner
approves a documented, time-bounded exception. Runtime dependencies are kept
minimal; Excel, Parquet, DOCX, PDF, plotting, and integration libraries remain
optional and are loaded only by the relevant feature.

CI audits dependencies, validates artifacts, exercises core and extras, and
tests clean wheel and sdist installation. PyPI publication uses GitHub OIDC
Trusted Publishing from the protected `pypi` environment, immutable action
revisions, least-privilege permissions, and provenance attestations.
