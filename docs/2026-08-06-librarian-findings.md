# The Librarian, run on this tree for the first time

Date: 2026-08-06
Subject: `simple-cmdb`, 38 knowledge items, one module
Tooling: `regen-librarian` 0.4.0 for the mechanical pass, then a reading pass over the full corpus

## Why this was worth doing

Every other check in this methodology looks at a change. Validation passed on this tree. Contracts passed. The debt report was clean. Nothing was watching for the failure that only appears when items are read against each other, which is the gap [REP-0006](https://github.com/tysoncung/regen.engineering/blob/main/reps/REP-0006-continuous-knowledge-operations.md) exists to close.

The mechanical pass found nine candidates, all minor: one duplication pair, three orphans, five assumptions with no review date. Nothing that would justify the tool.

The reading pass found six, including one confirmed data-loss defect and three items making factual claims that later work had already falsified. **Everything below was invisible to every existing check.**

## 1. Fixing ISS-102 turned ISS-104 from data-orphaning into data-deletion

**Confirmed by reproduction.**

ISS-104 is still open. It describes `INSERT OR REPLACE INTO servers` (still at app.py:398) deleting the conflicting row on rediscovery and inserting a new one with a new id, and states the consequence:

> The row gets a new `id`, so services attached to the old id are orphaned (ISS-102 means nothing cascades or complains)

That consequence was true when written. It is not true now. ISS-102 was resolved on 2026-07-31: every connection goes through `get_db()`, which issues `PRAGMA foreign_keys = ON` (app.py:35). The `services` table declares `ON DELETE CASCADE` on `server_id` (app.py:99), and `discovery_history` does the same (app.py:128).

With foreign keys enforced, the delete that REPLACE performs now fires those cascades. Reproduced against SQLite directly:

```
before rediscovery: server id=1, services=1
after  rediscovery: server id=2, services=0
```

So clicking "Discover Local" a second time on a known host no longer leaves its services orphaned. It **deletes them**, along with that server's discovery history. The open issue understates its own severity, in the direction that matters.

Neither issue is wrong on its own. ISS-102 correctly records what was fixed; ISS-104 correctly recorded what was true when it was written. The defect is in the relationship between them, and no check in this methodology looks at relationships between items.

**This is the finding that pays for the Librarian.** A fix to one issue silently made a different open issue worse, and the only way to see it was to read both.

## 2. Three items disagree about what the application binds to

| Item | Claim |
|---|---|
| ASM-102 (draft) | "the app binds 0.0.0.0 by default (app.py:850-852)" |
| RISK-101 (active) | "the app binds `0.0.0.0` by default (app.py:850-852)" |
| RISK-102 (active) | "the app binds 127.0.0.1 unless CMDB_HOST is set" |

The code agrees with RISK-102: `host = os.environ.get('CMDB_HOST', '127.0.0.1')` (app.py:875). RISK-102's own mitigation note is what changed it, on 2026-07-31.

This matters beyond tidiness. RISK-101 is rated **likelihood: high**, and the stated reason is:

> Likelihood is rated high because the default configuration, followed literally, exposes the API to the LAN.

The default configuration no longer does that. The rating rests on a fact that the mitigation recorded one item away invalidated, so the risk register currently overstates this risk. A stale fact is bad; a stale fact load-bearing for a severity rating is worse, because it distorts what gets attention next.

All three items also cite app.py:850-852, which now holds different code. Line citations rot silently.

## 3. ASM-105 cites the exact line that disproves it

ASM-105 is `status: active` and says "Confidence: high":

> app.py reads only `PORT` and `DOCKER_CONTAINER`; the DB path is hardcoded `cmdb.db`, app.py:24

app.py:24 now reads:

```python
DB_PATH = os.environ.get('CMDB_DB', 'cmdb.db')
```

The database path is configurable, and has been since the mitigation work. The application now reads `CMDB_DB`, `PORT`, `FLASK_DEBUG`, and `CMDB_HOST`. `DOCKER_CONTAINER` is gone entirely.

The item's *conclusion* survives: the README still documents `DATABASE_PATH` and `FLASK_ENV` (README.md:167-168), and the application reads neither. But the mismatch has changed shape into a worse one. Previously the README promised configurability that did not exist. Now the configurability exists under a different name, so a reader who follows the README sets `DATABASE_PATH`, gets silently ignored, and never learns that `CMDB_DB` would have worked.

A high-confidence assumption whose evidence has quietly inverted is more dangerous than a low-confidence one, because nobody rechecks it.

## 4. CT-109 is the only place a real limit is written down

CT-109 asserts:

> the body is {"history": [...]} with **at most 20 items**, newest first

The code confirms it: `LIMIT 20` in the history query. But CT-109 verifies BR-107, and BR-107 describes only what `POST /api/discover/local` does. Nothing in it mentions the history endpoint's page size.

So the 20-item cap exists in this tree only inside a contract. Contracts are meant to verify rules, not to be the sole home of one. An agent regenerating from the rules would not know to cap the query, the contract would then fail, and the failure would look like a regeneration defect rather than what it is: knowledge that was never written as knowledge.

Worth noting alongside it that BR-107 contains a *different* twenty ("at most 20 processes", in the stored blob). Two unrelated twenties in adjacent items is a trap for the next reader, and it is exactly the pattern the mechanical tension check is built to notice, which it did not here because neither is stated as a bound the other exceeds.

## 5. A superseding rule left in draft leaves a hole

ASM-103 is `status: superseded`. BR-110 declares `supersedes: ASM-103` but is itself `status: draft`.

Nothing active describes classification-field behaviour. The assumption has been retired in favour of a rule nobody has agreed to, so if BR-110 is rejected or amended, the tree has no current account of how `status`, `environment`, and `criticality` actually behave.

Contrast ASM-101 and BR-109, where the superseding rule is `active`. That pair is fine, which is what makes the other one visible.

ASM-104 has a milder version of the same problem: it records the intent behind the foreign key declarations, ISS-102's fix implemented exactly that intent, and ASM-104 is still `draft`. Its confidence should have moved.

**Suggested rule, if this generalises:** an item may not be marked `superseded` until the item superseding it is `active`. That is mechanically checkable and belongs in the validator rather than here.

## 6. Six resolved issues are marked `deprecated`, because nothing better exists

ISS-101, ISS-102, ISS-103, ISS-105, ISS-107, and ISS-108 all carry `status: deprecated` and all say "Resolved <date> in <branch>" in the body.

Deprecated ordinarily means still present and discouraged. These are fixed and gone. A reader filtering on status cannot tell "we fixed this" from "we advise against this", and the two call for opposite actions.

This one is not really a defect in the tree. The schema's status enum is `draft | active | deprecated | superseded`, with no `resolved`, so whoever wrote these picked the closest available word. That is a **schema gap**, and it is filed upstream rather than fixed here.

## What the mechanical pass got right, and what it missed

Worth stating both, since the split between the two halves is the design claim being tested.

It **found**: three genuine orphans (ISS-103, ISS-107, RISK-103, all confirmed unreferenced), five assumptions with no review date, and one fair duplication candidate.

It **missed everything above**, and would have gone on missing it however long it ran. Not one of the six is structurally malformed. Every item is individually valid, correctly linked, and schema-clean. Four of the six are cases where an item was true when written and was falsified by later work, which is a category no validator can hold an opinion about, because the item does not change when the world does.

It also produced one **false positive** during development, before being fixed: ADR-103 was reported as referenced by nothing, when the module overview names it. The citation graph only scanned item files. A tool that invents orphans gets switched off, so that now has a test.

## Cost

The mechanical pass is free and takes under a second. The reading pass consumed roughly 40,000 characters of corpus, once, and produced six findings of which four are worth acting on. That is a favourable ratio, but this tree is 38 items. The interesting question is whether it still holds at 400, and this run says nothing about that.
