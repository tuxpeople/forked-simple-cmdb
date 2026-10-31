# Homelab inventory synchronization requirements

Date: 2026-10-31. Status: proposed requirements, not implemented.

## Context and boundary

Ansible in `~/development/github/tuxpeople/homelab-automation/` already reports hosts
through `POST /api/server/upsert`. A future independent reconciliation job should
also maintain applications, service instances and their dependencies. CMDB downtime
must not block infrastructure provisioning, configuration or destruction.

The cross-system design is recorded in the Personal Obsidian vault at
`📚 Wissen/💻 IT/Homelab/Architektur/CMDB und IPAM Integration.md`.
IPAM integration and UniFi DHCP configuration are outside this repository's scope.
The UDM owns DHCP leases and reservations; a separate UniFi Terraform root is being
expanded. Do not introduce Terraform callbacks as a prerequisite for this API.

## Current local implementation

`app.py` provides a hostname-based server upsert. Applications and services have
list/create/update/delete APIs, but no upsert. Dependencies have an add API, but
no dedicated reconciliation API. Service and dependency tables lack appropriate
unique synchronization keys. Applications store `version`; services do not.

Server upsert supports partial payloads but currently reports `updated: true` even
when supplied business values do not change. The existing Ansible reporter does
not submit `last_seen`; define observation timestamp behavior explicitly rather
than treating every inventory import as a successful runtime observation.

## Required API behavior

- Add application, service and dependency upserts, following the existing API
  conventions. Suggested paths: `/api/application/upsert`, `/api/service/upsert`,
  `/api/dependency/upsert`; exact contracts remain to be finalized.
- Enforce identity uniqueness in the database, not only via a preliminary lookup.
  Repeated and concurrent requests must not create duplicates.
- Return the stable object ID and distinguish creation, meaningful update and
  unchanged data. Track observation refreshes separately from configuration changes.
- Update only explicitly supplied fields. Preserve omitted manual fields; define
  explicit `null` clearing and reject nulls for required identity fields.
- Support reading managed objects and deleting obsolete dependencies through
  dedicated endpoints. Do not require bulk export/import or direct DB access.
- Validate referenced objects, dependency types and direction; reject invalid
  references and self-dependencies. Decide explicitly whether cycles are permitted.
- Apply the existing API authentication mechanism to all new endpoints.

## Identity, ownership and lifecycle

Add dedicated external identity and management metadata to synchronized objects,
including hosts and relationships. Proposed fields are `external_id`, `managed_by`
and, where useful, `last_seen` and lifecycle timestamps. Scope uniqueness by source
as needed. `owner` should represent a responsible person/team, not the collector.
Migrate the current `owner: ansible` convention compatibly rather than changing it
silently. `managed_by` identifies ownership but does not replace authorization.

Example external service key: `ansible:core1:pihole`; relation identity can use the
source service, target service and dependency type. Final key rules must account
for renames, multiple instances and replacements. Keep display names separate from
identity. Existing hostname-based host upsert must remain backward compatible.

Only automation-owned objects and fields may be reconciled automatically. Missing
objects may be retired only after a complete successful snapshot of their own
source/scope. An unreachable host, partial Ansible run or unavailable source is not
evidence of deletion. Prefer retirement before permanent deletion, with configurable
retention. Do not overwrite manual descriptions, criticality or ownership without
explicit field ownership rules. Lifecycle state and observed health are separate.

## Version belongs to the service instance

Add an optional service `version`, exposed in relevant read/write APIs and service
details. One application represents the product; services represent deployments:

- Application: Pi-hole.
- Service on core1: Pi-hole, version A.
- Service on core2: Pi-hole, version B.

Keep application `version` initially for compatibility; it must not be interpreted
as the installed version of every service. Do not automatically copy a potentially
ambiguous application version into existing services. Unknown versions remain unset.
Container tags/digests may be recorded separately later; avoid requiring them now.

## Useful service and dependency metadata

Support linking a service to its application and host during upsert, resolving
stable external references to internal IDs. Existing service PUT cannot currently
change these associations; address relocation/reassociation explicitly. URL/endpoint
metadata is useful alongside port/protocol; confirm the smallest model addition.
Application repository/documentation columns exist but are not currently writable
through the normal application create/update handlers; expose them if used by sync.

Represent dependencies as directed edges: source requires target. Distinguish runtime,
startup/deployment and optional dependencies. For example, an image registry may be
required to deploy a service without being necessary for an already running process.
Removing an edge from a complete managed declaration must remove only that managed
edge, preserving manually maintained relationships. Generic infrastructure
dependencies should be added only when they help assess impact or recovery.

## Implementation approach and acceptance criteria

Keep patches additive and small, following `AGENTS.md`; no broad refactor or new
dependencies are assumed. Define the contracts first and use a migration compatible
with existing databases. Do not reset the database. Resolve pre-existing duplicate
services/edges before enforcing unique constraints; do not silently discard data.
Update README/API notes when behavior is implemented.

- [ ] Repeat application/service/dependency upserts without duplicate rows.
- [ ] Concurrent upserts respect database uniqueness.
- [ ] Omitted fields survive; explicit clears follow the documented contract.
- [ ] Two instances of one application retain independent versions.
- [ ] Existing hostname-based host reporting remains compatible.
- [ ] Invalid references, self-edges and unsupported types fail clearly.
- [ ] Obsolete managed edges can be removed without affecting manual edges.
- [ ] Source-scoped retirement does not treat partial or failed collection as deletion.
- [ ] Authentication applies consistently; credentials are never stored in metadata.
- [ ] Existing populated databases upgrade without data loss.

After these changes, integration work resumes in homelab-automation with preview-only
host/IP reporting first, then Pi-hole services on core1/core2, then dependencies and
controlled retirement. This document records requirements, not a deployed feature.
