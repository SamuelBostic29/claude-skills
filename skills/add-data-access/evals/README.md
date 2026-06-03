# Evals for `add-data-access`

## What this skill is supposed to fix

Without this skill, Claude writes a clean but *generic* DAO from memory — wrong
concurrency control, wrong cache-key shape, string-interpolated queries, a
made-up wiring scheme — that doesn't match the repo. With it, Claude reads the
nearest existing DAO first and mirrors it, so the new persistence code is
indistinguishable from the repo's own, and it stops at the data-access layer
instead of also building the service / route / tests.

## How to run

1. Install the skill: `cp -r skills/add-data-access ~/.claude/skills/`
2. In a fresh session inside a repo that has at least one real DAO/repository,
   run each case below.
3. Compare the result to **Expected**. A case passes only if every checkbox holds.

## Cases

### Case 1 — New model + DAO, mirrors the reference (positive)

- **Setup / fixture:** A repo with at least one existing DAO/repository and its model.
- **Prompt:** "Add data access for a new `Widget` entity."
- **Expected:**
  - [ ] Reads an existing DAO and its model *before* writing anything.
  - [ ] New model uses the same base type / typing / serialization as existing models.
  - [ ] New DAO matches the reference's pk/partition handling, optimistic concurrency, cache keys + invalidation, parameterized queries, and field allowlists.
  - [ ] No business logic, HTTP types, or tests appear in the DAO.
  - [ ] Reports which DAO it mirrored.

### Case 2 — One new method on an existing DAO (positive)

- **Setup / fixture:** A resource that already has a DAO.
- **Prompt:** "Add a `get_by_<field>` query to the `Widget` DAO."
- **Expected:**
  - [ ] Adds a single method to the existing DAO; does NOT create a new class or file.
  - [ ] Method mirrors sibling methods (parameterized query, cache usage, allowlist updated if the new field needs it).
  - [ ] Stops without touching the service, route, or tests.

### Case 3 — Wrong layer (negative / should defer)

- **Setup:** Same repo.
- **Prompt:** "Add the API endpoint and request validation for `Widget`."
- **Expected:**
  - [ ] Recognizes this is the controller/service layer, not data access.
  - [ ] Defers to **add-controller** / **add-service** instead of building a DAO.
  - [ ] Does not scaffold persistence code.

### Case 4 — No DAO to mirror (negative / should ask)

- **Setup:** A repo (or area) with no existing DAO/repository to use as a reference.
- **Prompt:** "Add data access for `Widget`."
- **Expected:**
  - [ ] Notes there is no existing DAO to mirror.
  - [ ] Asks how persistence should be structured rather than inventing a house style.
