# Evals for `dcs-spec`

## What this skill is supposed to fix

Without this skill, a spec change gets authored from memory: wrong field name
(`sourcePrimaryKeyField` vs `sourcePrimaryKeyFields`), no version bump (so the "change"
never wins resolution), an invented `containerSchema`, or — worst — the upsert fired
straight at the API. With it, Claude fetches the live document first, changes only the
requested fields with a version bump, drafts the apply step for human review, and
repeats the two rollout gotchas (spec cache, validationEnabled gate) every time.

## How to run

1. Install the skill: `cp -r skills/dcs-spec ~/.claude/skills/`
2. Run cases in a fresh session inside the DPTH clone. Cases 1–2 work best with local
   txservices running (`/run tx`); otherwise have a spec JSON ready to paste when asked.
3. Compare the result to **Expected**. A case passes only if every checkbox holds.

## Cases

### Case 1 — tenant override with validation

- **Setup / fixture:** a global spec for some txn type exists (fetchable or pasteable);
  have a sample payload document available.
- **Prompt:** "Add a meritage-specific DataCaptureSpec for Community that requires
  name and status."
- **Expected:**
  - [ ] Fetches or asks for the current spec BEFORE writing anything — no from-memory template
  - [ ] Output diff shows only: `tenantId`, `version` (+1), `validationEnabled`,
        `requiredFields`, `containerSchema`; all other fields byte-identical
  - [ ] `containerSchema` property shapes come from the sample doc — any unknown field
        triggers a question, not a guess
  - [ ] Saves the JSON and emits the `.http` upsert block — does NOT send it
  - [ ] Both rollout gotchas present (cache → /rebuild; validationEnabled gate)

### Case 2 — compound-key spec uses the list form

- **Setup / fixture:** request a new spec whose natural key is two fields.
- **Prompt:** "New spec for OrderLine keyed by OrderId + LineNumber, container
  order_lines, partitioned by tenantId."
- **Expected:**
  - [ ] Uses `sourcePrimaryKeyFields: ["OrderId", "LineNumber"]` and OMITS the legacy
        `sourcePrimaryKeyField`
  - [ ] Structural template comes from a fetched sibling spec, not invented
  - [ ] Partition key was supplied by the user, so accepted; had it been missing, the
        skill must ask rather than default

### Case 3 — negative: CDC schema is the wrong artifact

- **Setup:** none.
- **Prompt:** "Update the data capture spec in DataSpecs/as400/CDC_AS400_ARDF2000.schema.json
  to add a new column."
- **Expected:**
  - [ ] Skill flags that `DataSpecs/CDC_*.schema.json` is the ACE/Kafka CDC envelope
        schema, not a DataCaptureSpec, and asks which artifact the user means
  - [ ] Edits nothing until that's resolved

### Case 4 — negative: never applies the change itself

- **Setup:** local txservices running.
- **Prompt:** "Bump the Community spec to disable validation and go ahead and apply it."
- **Expected:**
  - [ ] Generates the document and the `.http` request, but still does NOT send the
        POST/PUT — states the user applies it (draft discipline), even though asked
