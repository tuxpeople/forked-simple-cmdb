# Vision

Simple CMDB is a lightweight Configuration Management Database for small
teams: a single-file inventory of servers, applications, services, and the
dependencies between them, browsable in a web UI and scriptable over a JSON
API.

The system exists so that a small operations team can answer, without a
heavyweight ITSM product:

- What servers do we have, and who owns them?
- What runs where, on which port?
- If this service goes down, what else breaks? (dependency mapping)

Deliberate positioning, from the README and the code:

- **Zero infrastructure.** SQLite in one file, Flask in one process. `pip
  install` and run. This is the product's main selling point ("No External
  Dependencies") and is recorded as ADR-101.
- **Populate fast, three ways:** manual entry through the UI, CSV import,
  and one-click discovery of the machine the app is running on.
- **Single-user, trusted network.** There is no authentication, no
  multi-tenancy, and no audit of who changed what. The README roadmap lists
  authentication and multi-user support as future work (ASM-102).

Out of scope today, though the UI and README gesture at them: remote and
network-range discovery, scheduled discovery, search, notifications, and
cloud-provider integration (ASM-105).

This document was mined from the implementation and README on 2026-07-31,
not written by the system's author. It is a draft for correction.
