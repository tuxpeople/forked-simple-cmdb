---
id: RISK-102
type: risk
title: Debug mode is the default outside Docker
status: active
since: 2026-07-31
likelihood: medium
impact: high
mitigation: Default debug to off; opt in via an env var instead of opting out via DOCKER_CONTAINER
affects: [cmdb]
---

`python app.py` runs Flask with `debug=True` on `0.0.0.0` unless the
`DOCKER_CONTAINER` env var is set (app.py:849-852). The Werkzeug debugger
that ships with debug mode allows arbitrary code execution from the
browser on any unhandled exception page (PIN-gated, but the PIN is
printed to the console and brute-forceable), and ISS-101 provides a
reliably crashing endpoint to reach it.

The README's quick start is exactly this exposed configuration.

Confidence: high for the facts; likelihood medium because it requires a
reachable network position, which ASM-102 says should not exist but
nothing prevents.
