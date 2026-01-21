# AGENTS.md - Forked Simple CMDB

Local project instructions for working on this fork while staying upstream-friendly.

## Upstream-Friendly Changes

- Keep patches small, additive, and focused on `app.py` or small helper modules.
- Avoid large refactors or template/UI changes unless necessary.
- Prefer environment-driven configuration over hard-coded values.
- Use guarded behavior (feature flags, optional defaults) to reduce conflicts.
- Rebase your feature branch on `main` regularly; resolve conflicts there.
- Keep changes in a small number of commits to ease rebases.

## Repo Hygiene

- Keep documentation in English.
- If behavior changes, update `README.md` or API notes.
- Do not add or remove dependencies unless required.
