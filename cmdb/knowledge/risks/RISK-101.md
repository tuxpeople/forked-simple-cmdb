---
id: RISK-101
type: risk
title: No authentication on destructive endpoints
status: active
since: 2026-07-31
likelihood: high
impact: high
mitigation: Put the app behind authenticating reverse proxy, or bind to localhost until auth ships
affects: [cmdb]
---

Every mutating endpoint (add, update, delete, import, discovery) is
unauthenticated, and the app binds `0.0.0.0` by default (app.py:850-852),
so any peer that can reach the port can delete the entire inventory with a
handful of DELETE requests, or poison it via import.

Under ASM-102 (trusted network) this is tolerable; the risk is that
nothing enforces or even documents that boundary, and the Docker
instructions publish the port. Likelihood is rated high because the
default configuration, followed literally, exposes the API to the LAN.

Confidence: high; directly observable in code and Dockerfile.
