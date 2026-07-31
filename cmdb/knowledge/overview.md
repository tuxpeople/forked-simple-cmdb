# cmdb

The whole application is one module: a Flask app (`app.py`, ~850 lines) over
five SQLite tables (`servers`, `applications`, `services`, `dependencies`,
`discovery_history`), serving both a server-rendered HTML UI and a JSON API.

This overview, like everything in this package, is a mined draft
(2026-07-31). Statements carry their evidence; corrections are welcome and
are the point.

## Responsibilities

- Inventory CRUD for servers, applications, services over the JSON API
- Directed service-to-service dependency records
- One-click discovery of the local host (hardware facts, processes,
  listening ports) into the inventory plus a history trail
- CSV export of all four inventory tables; CSV import of servers and
  applications
- Aggregate statistics for the dashboard and for integration

## Out of scope

- Authentication and authorization: none exists (RISK-101, ASM-102)
- Remote/network discovery: the UI shows a form but tells you it is not
  implemented (`templates/discover.html`)
- Update of services' server/application links, or of dependencies: no
  endpoint edits `services.server_id`/`application_id`, and dependencies
  have add and read but no update or delete over HTTP

## Interface

The authoritative wire-format contract is [`api.openapi.yaml`](api.openapi.yaml)
in this package (REP-0002). The table below is a human summary; where they
disagree, the OpenAPI file wins.

All success responses are HTTP 200 (never 201/204) and most bodies use a
`{"success": true|false, ...}` envelope; see ADR-103 and the OpenAPI file
for the exceptions.

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/discover/local` | Discover the machine the app runs on; upsert it as a server. 200 or 500 |
| POST | `/api/server/add` | Add a server. Body requires `hostname`. 200, 400 on duplicate |
| PUT | `/api/server/{server_id}` | Replace a server's editable fields. 200, 404 |
| DELETE | `/api/server/{server_id}` | Hard-delete a server. 200, 404 |
| POST | `/api/application/add` | Add an application. Body requires `name`. 200, 400 on duplicate |
| PUT | `/api/application/{app_id}` | Replace an application's editable fields. 200, 404 |
| DELETE | `/api/application/{app_id}` | Hard-delete an application. 200, 404 |
| POST | `/api/service/add` | Add a service. Body requires `server_id`, `service_name`. 200 |
| PUT | `/api/service/{service_id}` | Replace a service's editable fields. 200, 404 |
| DELETE | `/api/service/{service_id}` | Hard-delete a service. 200, 404 |
| POST | `/api/dependency/add` | Add a dependency edge. Requires `source_service_id`, `target_service_id`. 200 |
| GET | `/api/stats` | Aggregate counts and breakdowns. 200 |
| GET | `/api/discovery/history` | Last 20 discovery runs. Currently always 500 (ISS-101) |
| GET | `/api/export/{table}` | CSV download of one of the four inventory tables. 200, 400 |
| POST | `/api/import/{table}` | CSV upload into `servers` or `applications`. 200, 400 |

### HTML page routes (out of contract scope)

These render the UI and are deliberately **not** part of the API contract;
they may change with the templates: `GET /`, `/servers`,
`/server/<id>`, `/applications`, `/application/<id>`, `/services`,
`/service/<id>`, `/dependencies`, `/discover`. Unknown `<id>` on the detail
pages returns a plain-text 404 (`"Application not found"`,
`"Service not found"`); `GET /server/<unknown>` currently renders the
template with a null server rather than 404 (app.py:163-181).

### Error bodies

Two shapes exist, and the inconsistency is real, not a typo in this doc:

- Most endpoints: `{"success": false, "error": "<message>"}` with 400, 404
  or 500
- Export/import guards: `{"error": "Invalid table"}` / `{"error": "No file
  provided"}` with 400 and no `success` key

Unhandled exceptions inside handlers are caught and become 500 with the
exception's string in `error`, which leaks internals (e.g. a missing
required field surfaces as `"error": "'server_id'"` from the KeyError).
Requests to the JSON endpoints without a JSON content type fail before the
handler runs and return Flask's default HTML 415 page, not JSON.
