---
name: dcs-spec
version: 1.0.0
description: |
  Author or modify a DataCaptureSpec for the Data Plane Transaction Hub —
  the Cosmos documents (container "DataCaptureSpecs") that drive how txservices
  validates, keys, partitions, and stores each transaction type. Use when asked
  to "add/change a data capture spec", "onboard a new txn type / entity",
  "add a tenant override", "enable validation for <entity>", or "/dcs-spec".
  Generates the spec document grounded in the current one (never from memory),
  drafts the upsert call without sending it, and flags the spec-cache gotcha.
allowed-tools:
  - Read
  - Grep
  - Glob
  - AskUserQuestion
  - Write
  - Bash(curl:*)
---

# Dcs-spec: author a DataCaptureSpec change, grounded in the live one

A DataCaptureSpec decides, per transaction type, which Cosmos container a document lands in, what its primary/partition keys are, which filters and sorts the API allows, and whether/how payloads are validated. Getting one subtly wrong corrupts data routing for every write of that type. Your job: produce a correct spec document (and `containerSchema` when validation is involved) derived from the **current live spec**, plus a ready-to-review upsert call. The failure mode to guard against is authoring from memory — field names like `sourcePrimaryKeyFields` vs the legacy `sourcePrimaryKeyField` have load-bearing differences, so the current document is always fetched first.

Two artifacts share the word "spec" in this repo — don't conflate them:

- **DataCaptureSpec** (this skill): runtime Cosmos document, served by `/1.0/data-capture-specs`, consumed by `txservices`/`search` via `datastore/data_capture_specs/data_capture_spec_loader.py`.
- **`DataSpecs/<source>/CDC_*.schema.json`**: draft-07 JSON Schemas for the Debezium CDC envelopes consumed by the **ACE/Kafka inbound** layer. Changing entity capture behavior there is an ACE-side change with its own configs — if the request points at these, say so and confirm which artifact is meant before touching anything.

For the full field catalog, resolution semantics, and a worked example, read `references/spec-fields.md`.

## When to use this skill

- "Add / change a DataCaptureSpec", "onboard a new transaction type or entity"
- "Add a tenant-specific override for <txn type>", "point <entity> at a different container"
- "Enable validation / add required fields / allow a new filter for <entity>"

## When NOT to use this skill

- **CDC envelope schemas** (`DataSpecs/CDC_*.schema.json`) — ACE-side artifact; coordinate with the ACE configs, different change process.
- **Writing the handler/DAO code that consumes specs** — that's ordinary DPTH Python work (python-for-dotnet conventions apply).
- **Applying the change to tst/prd** — this skill drafts; promoting specs across environments is the team's deploy process.

## Steps

1. **Classify the change.** New global spec, tenant override, or edit to an existing spec (validation toggle, filters, keys). If the txn type, tenant, or intent is unclear — AskUserQuestion and stop. **Partition-key and primary-key choices are never invented**: for a brand-new entity, those come from the user/team (they're a data-model decision with migration consequences).

2. **Fetch the current spec — ground truth, not memory.** Preferred: local txservices is running (check `.running-services.json` in the shared Logs root) → `curl` `GET /1.0/data-capture-specs` with the `X-BFS-Auth` header from `txservices/apis/.env`. Not running → ask the user to paste the current document (the team can pull it from Cosmos Data Explorer). For a brand-new spec, fetch the closest existing one as the structural template instead.

3. **Generate the new document.** Apply the change against the fetched JSON. Hard rules:
   - **Bump `version`** (new highest version wins resolution — see references); never mutate semantics in place at the same version.
   - Compound keys use `sourcePrimaryKeyFields` (list) and **omit** the legacy `sourcePrimaryKeyField` — the loader refuses to set a single PK for compound keys.
   - Tenant override: set `tenantId`; global spec: `tenantId` of `""` (the loader treats `""`/null/undefined as global).
   - `validationEnabled: true` requires a `containerSchema` (draft-07). Derive its properties from a real sample document or the existing schema — never from imagination; unknown fields → ask.
   - Keep every field you didn't intend to change byte-identical to the fetched spec.

4. **Draft the apply step — do not send it.** Save the document via Write (e.g. alongside the user's working files, named `<specName>-v<version>.json`) and output the upsert request in `.http` format (matching `txservices/api-local-testing.http` style) for the user to review and send.

5. **State the rollout gotchas** (both, every time): running services cache resolved specs — after applying, `/rebuild` the local service to pick the change up; and validation runs only where `validationEnabled` is true, so a spec change is silent for types still flagged off.

6. **Stop.** Done = generated document + drafted upsert + gotcha notes. Never POST/PUT the spec yourself, never edit Cosmos directly, never touch other specs.

## Output format

```
DataCaptureSpec change: <specName> — <new | tenant override for <tenant> | edit: <what>>
Based on: live spec version <N> (fetched <from local API | user-pasted>)
New version: <N+1>

<diff-style summary: only the fields that changed>

Saved: <path to the generated JSON>
Apply (review, then send yourself):
  <the .http request block>

After applying: /rebuild the service (spec cache), and note validationEnabled=<value>.
```

## Rules

### What to do

- **Always fetch before authoring.** Live spec or user-pasted document — the template is never reconstructed from memory.
- **Version-bump every semantic change.** Resolution is `ORDER BY c.version DESC` — the bump *is* the deployment.
- **Minimal diff.** Only the requested fields change; the summary shows exactly which.
- **Ask on data-model decisions.** New partition keys, new primary keys, new containers — user decides, skill drafts.

### What NOT to do

- **NEVER send the upsert.** Draft means draft — the user reviews and applies.
- **NEVER invent `containerSchema` properties or key fields.** Unknown shape → ask for a sample document.
- **Don't edit `DataSpecs/CDC_*.schema.json`** under this skill — wrong artifact (see the disambiguation above).
- **Don't "clean up" the fetched spec** — unknown-looking fields may be consumed by ACE or other services; they ride along unchanged.

### Format discipline

- Lead with the change summary and version line; the full document goes to the saved file, not the chat.
- Both rollout gotchas appear in every output, one line each — no essays.
