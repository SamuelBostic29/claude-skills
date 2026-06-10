---
name: api-verify
version: 1.0.0
description: |
  Live HTTP smoke-verification for the Data Plane Transaction Hub: prove a code
  change actually works by driving real requests against a locally running DPTH
  service (txservices, search, mulesoft/Rx) and reading its run log. Use when
  asked to "verify my change works", "hit the endpoint and check", "smoke test
  this before the PR", or "/api-verify" in DPTH. Handles the ETag GET→If-Match
  dance for writes. Local services talk to REAL shared dev Azure resources, so
  reads are free but writes require confirmation and cleanup.
allowed-tools:
  - Read
  - Grep
  - Glob
  - AskUserQuestion
  - Bash(curl:*)
---

# Api-verify: prove the change works against the running service

Tests passed and the code looks right — now show it actually behaves over HTTP. Your job is to design the smallest request sequence that exercises the change, run it against the **locally running** service, and report verified/failed with response and log evidence. The thing to never forget: a "local" DPTH service is only local at the HTTP layer — it reads and writes the **real shared dev Cosmos/Redis**. Reads are free; every write lands in data teammates use. Write-path verification therefore uses clearly-marked test documents, asks before the first write, and cleans up after itself.

## When to use this skill

- "Verify my change works" / "hit the endpoint and check" / "smoke test this" in DPTH
- After `/py-check` passes, before `draft-pr` — the behavioral proof step
- "Why is this endpoint returning X?" — reproduce with a real request + log capture

## When NOT to use this skill

- **Unit-level checking** — `/py-check` runs the test suites; this skill is for observed behavior.
- **The service isn't running** — start it with `/run <service>` first; this skill never launches services itself.
- **Anything pointed at tst/prd URLs** — local service only, hard boundary. Shared-environment verification is a team activity, not a skill run.
- **Non-DPTH services** — the .NET `verify` skill covers those repos.

## Service facts

- Ports and log files come from the running state: `C:\Users\Samuel.Bostic\Documents\Paradigm\Repos\WorkingFiles\Logs\.running-services.json` (canonical ports: DpthTxServices 5000, DpthSearch 5001, DpthRxServices 3002).
- Request conventions (txservices/search; see `txservices/api-local-testing.http` and `docs/api/tx-services.md`):
  - Headers: `TenantId: <tenant>` and `X-BFS-Auth: <key>` — the key is `TXSERVICES_API_KEY` in the service's `.env` (read it locally; never print it).
  - **ETag concurrency:** reads return an `ETag`; PUT/DELETE must echo it via `If-Match`. Missing → `428`; stale → `412 Precondition Failed`. A 412 mid-sequence means re-GET and retry once — that's the contract working, not a bug.
- The service's merged stdout/stderr log is `{LogsRoot}\{CanonicalName}-Logs\run-*.log` (newest file). Grep it — these are large.

## Steps

1. **Confirm the target is running.** Read `.running-services.json`; the service must be Healthy there. Not running → stop and say: start it with `/run <service>` (after a code change, `/rebuild <service>` so the change is actually loaded — verifying a stale process is the silent killer of this whole exercise; if in doubt about staleness, recommend `/rebuild` and stop).

2. **Design the smallest probe sequence for the change.** From the diff or the user's description, pick the endpoint(s) and the minimal calls that demonstrate the new behavior — prefer the read path. If the change is write-path, plan: `POST`/`GET` a **test document** (ids/names prefixed `apiverify-` so it's unmistakable), `PUT`/`DELETE` with the ETag dance, then cleanup `DELETE`. Use `api-local-testing.http` as the request-shape reference. Need a tenant for writes? Ask which tenant is safe to write under — never pick one.

3. **Gate writes.** Reads proceed freely. Before the first write, state the exact documents that will be created/modified/deleted in shared dev data and get a yes (AskUserQuestion). No yes, no writes — offer the read-only subset instead.

4. **Execute with curl** (Bash tool; one logical step per call), capturing status, headers (`-i` for ETag), and body. Note the timestamp before the first call so the log window is bounded.

5. **Check the log.** Grep the newest `run-*.log` for the window since step 4 started — stack traces, validation errors, cache-routing lines relevant to the change. A 200 with an error stack in the log is NOT verified.

6. **Clean up** every `apiverify-` document the sequence created (DELETE with the final ETag). Cleanup failure is reported loudly with the leftover ids — never silently abandoned.

7. **Report and stop.** Verdict + evidence per the Output format. Done = verdict delivered and cleanup confirmed. Do not fix code, do not restart services, do not widen the probe into exploratory testing.

## Output format

```
api-verify: <VERIFIED | FAILED | PARTIAL> — <service>, <change being verified>

Sequence (tenant: <tenant or n/a>):
1. GET /1.1/txns?TxnType=... → 200, 14 items, new field `Status` present ✓
2. PUT /1.1/txns/apiverify-001 (If-Match from step 1's ETag) → 200 ✓
3. GET (re-read) → 200, change persisted ✓
4. DELETE apiverify-001 → 204 (cleanup) ✓

Log: clean over the window (no tracebacks; spec resolution logged as expected)
   | <only lines that matter, if any>

Verdict: VERIFIED — <one line tying the evidence to the claimed change>
```

## Rules

### What to do

- **Verify the running code, not the edited code.** If the service started before the change, `/rebuild` first — this rule outranks convenience.
- **Smallest sequence that proves it.** Three purposeful calls beat fifteen exploratory ones.
- **Mark and clean test data.** `apiverify-` prefix on everything created; cleanup is part of the run, and leftovers are reported with ids.
- **Pair every response with the log.** HTTP status alone can lie (silent 200s with logged stacks).

### What NOT to do

- **NEVER write to shared dev data without the step-3 confirmation,** and never under a tenant you chose yourself.
- **NEVER point a probe at tst/prd.** Local ports only.
- **Don't print secrets.** `X-BFS-Auth` values are read from `.env` into the command, never echoed into output.
- **Don't keep retrying a failing call.** One 412 retry (re-GET → If-Match) is contract; anything else failing twice is a finding to report, not a thing to brute-force.

### Format discipline

- Verdict line first; numbered sequence with one line per call; log section only when it has signal.
- FAILED runs still include cleanup status — broken verification doesn't excuse leftover data.
