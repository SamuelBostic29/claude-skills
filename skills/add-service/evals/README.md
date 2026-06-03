# Evals for `add-service`

## What this skill is supposed to fix

Without this skill, Claude scatters business logic into the wrong layer — a fat
route handler, or a DAO that does orchestration — or writes a "service" that
reaches straight into the database and imports HTTP types. With it, Claude
mirrors the nearest existing service: logic lives in one place, data comes only
through repositories, and it stops at the service layer.

## How to run

1. Install the skill: `cp -r skills/add-service ~/.claude/skills/`
2. In a fresh session inside a repo that has a real service layer, run each case.
3. Compare the result to **Expected**. A case passes only if every checkbox holds.

## Cases

### Case 1 — New service orchestrating repos (positive)

- **Setup / fixture:** A repo with an existing service that depends on repositories/DAOs.
- **Prompt:** "Add a service for `Widget` that combines its repo with the pricing repo."
- **Expected:**
  - [ ] Reads an existing service (and its factory + repos) before writing.
  - [ ] New service injects repositories the same way the reference does.
  - [ ] Gets all data through repos — no direct DB/SDK calls, no HTTP types.
  - [ ] Matches DI/factory dispatch, async/sync style, pagination/result-shaping, error types.
  - [ ] Reports the service it mirrored and the repos it orchestrates.

### Case 2 — One method on an existing service (positive)

- **Setup / fixture:** A resource that already has a service.
- **Prompt:** "Add a `summarize_<X>` use case to the `Widget` service."
- **Expected:**
  - [ ] Adds a single method to the existing service; no parallel class.
  - [ ] Reuses the service's existing repo dependencies and helpers.
  - [ ] Stops without touching the DAO, route, or tests.

### Case 3 — Wrong layer: persistence (negative / should defer)

- **Setup:** Same repo.
- **Prompt:** "Write the query that fetches `Widget` rows by status."
- **Expected:**
  - [ ] Recognizes this is persistence, not business logic.
  - [ ] Defers to **add-data-access** instead of inlining a query in a service.

### Case 4 — No service layer to mirror (negative / should ask)

- **Setup:** A repo where controllers call DAOs directly and there is no service layer.
- **Prompt:** "Add a service for `Widget`."
- **Expected:**
  - [ ] Notes the repo has no service layer to mirror.
  - [ ] Asks whether a service layer should be introduced rather than inventing one.
