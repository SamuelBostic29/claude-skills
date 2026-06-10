# DataCaptureSpec — field catalog and resolution semantics

Ground truth: `txservices/apis/datastore/data_capture_specs/data_capture_spec_loader.py`
(`get_latest_data_capture_spec` + `build_txn_config_from_spec`). If this file and the
loader disagree, the loader wins and this file needs updating.

## Resolution: which spec a request gets

`get_latest_data_capture_spec(txn_type, tenant_id, datasource_id)` queries the
`DataCaptureSpecs` Cosmos container:

- Filter: `dataCaptureSpecName = <txn_type>`, then the **most specific combination the
  caller supplies** — tenant + datasource, tenant only, or (no tenant) *global-only*:
  `tenantId = '' OR IS_NULL OR NOT IS_DEFINED`.
- Winner: `ORDER BY c.version DESC`, `TOP 1` — **highest version wins**. That's why a
  semantic change is always a version bump: the new version *is* the cutover, and
  rolling back means writing a higher version with the old content (not deleting).
- No match → `ValueError` — there is no silent fallback from tenant-specific to global
  inside this function; callers decide what to pass.

## Field catalog

| Field | Type | Meaning / rules |
|---|---|---|
| `dataCaptureSpecName` | string | The txn type this spec governs; lookup key. |
| `tenantId` | string | `""` / absent = global spec; set = tenant override. |
| `dataSourceId` | string | Optional source-system qualifier; part of lookup when supplied. |
| `version` | number | Resolution winner — highest wins. Bump on every semantic change. |
| `containerName` | string | Target Cosmos container; defaults to `dataCaptureSpecName` when absent. |
| `sourcePrimaryKeyField` | string | **Legacy single-PK form.** Still honored when `sourcePrimaryKeyFields` is absent. |
| `sourcePrimaryKeyFields` | string[] | Preferred. One element → behaves like single PK. **Multiple elements (compound key) → the loader sets no single `primary_key_field`** — code paths that need one don't get one; don't also set the legacy field. |
| `isPrimaryKeyGenerationEnabled` | bool | Service generates ids for incoming docs. |
| `generatedIdPrefix` | string | Prefix for generated ids (with the flag above). |
| `partitionKeyField` / `partitionKeyValue` / `partitionKeyFields` | string / string / string[] | Partition strategy: single field, fixed value, or composite list. **Data-model decision — never invented by the skill; changing it on an existing container effectively orphans existing documents' partitions.** |
| `allowedFilters` | string[] | Query-string filters the txn API accepts for this type. |
| `allowedSortFields` | string[] | Sortable fields. |
| `requiredFields` | string[] | Fields the write path requires. |
| `containerSchema` | object | Draft-07 JSON Schema for payload validation. |
| `validationEnabled` | bool | **Defaults false.** Schema only enforced when true — flipping it on for a type with dirty producers starts rejecting their writes; coordinate. |

Unknown fields found in a fetched spec: keep them verbatim — other consumers (search
service, ACE tooling, scripts) may read keys txservices ignores.

## Worked example — tenant override enabling validation

Fetched global spec (version 3, abridged):

```json
{
  "dataCaptureSpecName": "Community",
  "tenantId": "",
  "version": 3,
  "containerName": "communities",
  "sourcePrimaryKeyFields": ["CommunityId"],
  "partitionKeyField": "tenantId",
  "allowedFilters": ["Status"],
  "validationEnabled": false
}
```

Requested: "meritage should validate Community payloads — name and status required."

Generated (only the intended fields differ; version bumped):

```json
{
  "dataCaptureSpecName": "Community",
  "tenantId": "meritage",
  "version": 4,
  "containerName": "communities",
  "sourcePrimaryKeyFields": ["CommunityId"],
  "partitionKeyField": "tenantId",
  "allowedFilters": ["Status"],
  "validationEnabled": true,
  "requiredFields": ["name", "status"],
  "containerSchema": {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
      "name": { "type": "string" },
      "status": { "type": "string" }
    },
    "required": ["name", "status"]
  }
}
```

(`name`/`status` property shapes came from a sample document the user supplied — if no
sample exists, that's an AskUserQuestion, not a guess.)

## Rollout reminders (repeat in every output)

1. **Spec cache:** running services resolve-and-cache specs; the change is invisible to
   them until restart — `/rebuild <service>` locally; redeploy/restart in shared envs.
2. **Validation gate:** `validationEnabled` defaults false — a beautiful
   `containerSchema` does nothing until the flag flips, and flipping it is a
   producer-facing behavior change.
