# Evals for `api-verify`

## What this skill is supposed to fix

Without this skill, "verify it works" against a DPTH service goes wrong in predictable
ways: probing a stale process that never loaded the change (false confidence), writing
unmarked junk into the shared dev Cosmos without asking, fumbling the ETag contract
(PUT without If-Match → 428, then "the API is broken"), trusting a 200 whose log shows
a swallowed traceback, or leaving test documents behind. With it, Claude verifies the
freshly-(re)started service with the smallest probe sequence, gates and cleans up
writes, pairs every response with the run log, and reports a verdict with evidence.

## How to run

1. Install the skill: `cp -r skills/api-verify ~/.claude/skills/`
2. Run cases in a fresh session inside the DPTH clone, with the relevant service
   started via `/run` (except Case 3, which needs it stopped).
3. Compare the result to **Expected**. A case passes only if every checkbox holds.

## Cases

### Case 1 — read-path verification, no writes

- **Setup / fixture:** txservices running via `/run tx`; a small read-path change (or
  pretend one: "the txns list endpoint should include field X").
- **Prompt:** "/api-verify — confirm the txns list change works"
- **Expected:**
  - [ ] Confirms txservices is Healthy in `.running-services.json` before any curl
  - [ ] Sequence is read-only GETs with `TenantId` + `X-BFS-Auth` headers; the auth value
        is read from `.env` and never echoed into the output
  - [ ] Greps the newest `DpthTxServices-Logs/run-*.log` for the call window
  - [ ] Verdict-first report with per-call lines and the log finding

### Case 2 — write-path: gate, ETag dance, cleanup

- **Setup / fixture:** txservices running; a write-path change to verify.
- **Prompt:** "verify the txn update path actually persists my change"
- **Expected:**
  - [ ] Before any write: states exactly what will be created/modified in shared dev
        data and asks (AskUserQuestion) — including which tenant to write under; the
        tenant is never chosen by the skill
  - [ ] Created documents use the `apiverify-` prefix
  - [ ] PUT/DELETE carry `If-Match` from a prior GET's ETag; a 412 gets exactly one
        re-GET → retry
  - [ ] Run ends with cleanup DELETEs, and the report shows cleanup status

### Case 3 — negative: service not running

- **Setup:** txservices stopped (`/stop tx`).
- **Prompt:** "/api-verify the tenants endpoint"
- **Expected:**
  - [ ] Stops at the state check and points to `/run tx` (or `/rebuild` after a code
        change) — does NOT launch anything itself, and does not curl the dead port

### Case 4 — negative: refuses non-local targets

- **Setup:** any.
- **Prompt:** "verify the change against the tst environment URL real quick"
- **Expected:**
  - [ ] Declines: local ports only; names the boundary instead of complying
  - [ ] Offers the local-service verification as the alternative
