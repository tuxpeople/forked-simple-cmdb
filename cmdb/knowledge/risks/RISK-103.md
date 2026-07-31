---
id: RISK-103
type: risk
title: Hardcoded placeholder SECRET_KEY
status: draft
since: 2026-07-31
likelihood: low
impact: low
mitigation: Load SECRET_KEY from the environment; generate one if absent
affects: [cmdb]
---

`app.config['SECRET_KEY'] = 'cmdb-secret-key-change-in-production'`
(app.py:21) is committed to a public repository. Today nothing uses
sessions or signing, so the exposure is latent rather than active, which
is why both likelihood and impact are rated low. The moment
authentication (on the README roadmap) adds session cookies, this becomes
a session-forgery risk without any code change to the key itself.

Confidence: high; single line of code, and grep shows no session/flash
usage anywhere.
