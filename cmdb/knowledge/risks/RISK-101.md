---
id: RISK-101
type: risk
title: No authentication on destructive endpoints
status: active
since: 2026-07-31
likelihood: medium
impact: high
mitigation: Put the app behind authenticating reverse proxy, or bind to localhost until auth ships
affects: [cmdb]
---

Every mutating endpoint (add, update, delete, import, discovery) is
unauthenticated, so any peer that can reach the port can delete the entire
inventory with a handful of DELETE requests, or poison it via import.

Under ASM-102 (trusted network) this is tolerable; the risk is that nothing
enforces or even documents that boundary, and the Docker instructions publish
the port.

Likelihood lowered from high to medium on 2026-08-06. The high rating rested on
"the default configuration, followed literally, exposes the API to the LAN",
which stopped being true when RISK-102's mitigation landed on 2026-07-31:
`host = os.environ.get('CMDB_HOST', '127.0.0.1')` (app.py:875). Reaching the
API now takes a deliberate `CMDB_HOST=0.0.0.0`, which the Docker image sets, so
the containerised path remains exposed and the impact is unchanged.

That the rating outlived its own justification by six days, one item away from
the mitigation that invalidated it, is the finding rather than a footnote.

Confidence: high; directly observable in code and Dockerfile.
