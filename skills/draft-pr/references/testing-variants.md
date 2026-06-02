# Testing-section variants

Read this only after step 3 of `SKILL.md` has determined which variant applies. Use the matching format for the `## Testing` section of the PR description. Keep all values generic — `<PLACEHOLDER>` for anything project-specific. Omit the section entirely if the user chose "No testing section."

## API endpoint testing

````markdown
### API

**Endpoint:** `<METHOD> <path>`

**Payload:**
```json
{
  "<field>": "<value>"
}
```
````

If multiple endpoints are affected, list each with its own payload.

## In-app / UI testing

```markdown
### In the App

**Navigate:** <path to the feature, e.g. Section > Subsection > Detail>

**Steps:**

1. <Action and what to verify>
2. <Action and what to verify>
3. <A negative/validation case>
```

## Data-migration verification

Include pre/post verification queries and a results table.

````markdown
### Step 1 — Pre-migration: establish baseline

```sql
SELECT COUNT(*) FROM <table> WHERE <condition>;
```

### Step 2 — Run the migration

<How the migration is applied — e.g. deploy the service to run it at startup.>

### Step 3 — Post-migration: verify

```sql
-- Expected to differ from Step 1 in <way>
SELECT COUNT(*) FROM <table> WHERE <condition>;
```

### Results

| Metric | Pre | Post | Delta |
|--------|-----|------|-------|
| <metric> | <n> | <n> | <±n> |
````

## Infrastructure / config

```markdown
1. <Merge any dependency PR first, if applicable>
2. <Push a commit and verify the workflow/pipeline runs>
3. <Confirm expected behavior in logs / dashboard>
```
